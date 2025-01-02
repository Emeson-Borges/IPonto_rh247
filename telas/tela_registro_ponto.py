import flet as ft
import cv2
import base64
import hashlib
from threading import Thread
import time
import sqlite3
import os

# Carregar o classificador de rosto
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def processar_rosto(rosto):
    """Redimensiona e processa o rosto para gerar o hash."""
    rosto_redimensionado = cv2.resize(rosto, (100, 100))  # Redimensionar para tamanho fixo
    return rosto_redimensionado


def calcular_hash(rosto):
    """Calcula o hash SHA-256 do rosto processado."""
    rosto_em_bytes = rosto.tobytes()
    return hashlib.sha256(rosto_em_bytes).hexdigest()


def criar_tela_registro_ponto(page: ft.Page, db_path: str):
    if not os.path.exists(db_path):
        raise ValueError(f"Banco de dados não encontrado no caminho: {db_path}")

    status_text = ft.Text("Inicializando câmera...", size=20, weight="bold", color=ft.Colors.BLUE)
    camera_feed = ft.Image(width=300, height=300)
    timer_text = ft.Text("5 segundos restantes", size=18, weight="bold", color=ft.Colors.RED)
    stop_camera = False
    identificacao_realizada = False

    def update_images():
        """Captura frames da câmera, detecta rostos e registra o ponto."""
        nonlocal stop_camera, identificacao_realizada

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            status_text.value = "Erro: Não foi possível acessar a câmera."
            status_text.color = ft.Colors.RED
            page.update()
            return

        status_text.value = "Câmera iniciada. Posicione seu rosto..."
        status_text.color = ft.Colors.GREEN
        page.update()

        start_time = time.time()

        while not stop_camera:
            ret, frame = cap.read()
            if ret:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

                for (x, y, w, h) in faces:
                    # Extrair o rosto detectado
                    rosto_capturado = gray_frame[y:y + h, x:x + w]
                    rosto_processado = processar_rosto(rosto_capturado)
                    rosto_hash = calcular_hash(rosto_processado)

                    print(f"Hash gerado para verificação: {rosto_hash}")  # Debug

                    # Buscar no banco pelo hash
                    pessoa = buscar_funcionario_por_hash(cursor, rosto_hash)
                    if pessoa:
                        identificacao_realizada = True
                        registrar_ponto(conn, pessoa["nome"], pessoa["matricula"], rosto_hash, "Entrada")
                        exibir_confirmacao(f"Ponto registrado: {pessoa['nome']} ({pessoa['matricula']})")
                        stop_camera_feed(None)
                        return

                    # Desenhar uma elipse maior no rosto
                    cv2.ellipse(frame, (x + w // 2, y + h // 2), (int(w * 0.7), int(h * 0.7)), 0, 0, 360, (0, 255, 0), 3)

                _, buffer = cv2.imencode(".jpg", frame)
                frame_base64 = base64.b64encode(buffer).decode("utf-8")
                camera_feed.src_base64 = frame_base64
                page.update()

            elapsed_time = time.time() - start_time
            remaining_time = max(0, 5 - int(elapsed_time))
            timer_text.value = f"{remaining_time} segundos restantes"
            page.update()

            if elapsed_time >= 5 and not identificacao_realizada:
                stop_camera_feed(None)
                emitir_alerta("Funcionário não cadastrado. Por favor, entre em contato com o RH.")
                return

            time.sleep(0.03)

        cap.release()
        conn.close()

    def buscar_funcionario_por_hash(cursor, hash_encoding):
        """Busca o funcionário no banco de dados pelo hash."""
        try:
            cursor.execute("SELECT nome, matricula FROM dados_faciais WHERE hash_encoding = ?", (hash_encoding,))
            resultado = cursor.fetchone()
            if resultado:
                return {"nome": resultado[0], "matricula": resultado[1]}
            return None
        except Exception as e:
            emitir_alerta(f"Erro ao buscar funcionário: {e}")
            return None

    def registrar_ponto(conn, nome, matricula, hash_encoding, tipo):
        """Registra o ponto no banco de dados."""
        try:
            data_hora = time.strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""
                INSERT INTO registros_ponto (nome, matricula, data_hora, tipo, sincronizado)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, matricula, data_hora, tipo, "Não"))
            conn.commit()
        except Exception as e:
            emitir_alerta(f"Erro ao registrar ponto: {e}")

    def emitir_alerta(mensagem):
        """Exibe um alerta e redireciona para a tela inicial ao fechar."""
        def fechar_dialog(e):
            page.dialog.open = False
            page.go("/")
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Alerta"),
            content=ft.Text(mensagem),
            actions=[ft.TextButton("OK", on_click=fechar_dialog)],
        )
        page.dialog.open = True
        page.update()

    def exibir_confirmacao(mensagem):
        """Exibe uma mensagem de confirmação ao registrar o ponto."""
        def fechar_dialog(e):
            page.dialog.open = False
            page.go("/")
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Sucesso"),
            content=ft.Text(mensagem),
            actions=[ft.TextButton("OK", on_click=fechar_dialog)],
        )
        page.dialog.open = True
        page.update()

    def start_camera():
        """Inicia a câmera automaticamente."""
        nonlocal stop_camera
        stop_camera = False
        Thread(target=update_images, daemon=True).start()

    def stop_camera_feed(e):
        """Interrompe a câmera."""
        nonlocal stop_camera
        stop_camera = True
        status_text.value = "Câmera pausada."
        status_text.color = ft.Colors.BLUE
        page.update()

    start_camera()

    return ft.View(
        route="/registro_ponto",
        controls=[
            ft.Column(
                controls=[
                    camera_feed,
                    timer_text,
                    status_text,
                    ft.ElevatedButton(
                        text="Voltar",
                        on_click=stop_camera_feed,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
    )