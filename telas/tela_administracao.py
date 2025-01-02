import flet as ft

def criar_tela_administracao(page):
    # Função para voltar à tela principal
    def voltar(e):
        page.go("/")

    # Função para criar os cards com navegação
    def criar_card(icone, texto, rota):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(name=icone, size=40, color=ft.colors.BLUE),
                    ft.Text(value=texto, size=14, weight="bold", text_align="center"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,  # Centraliza no eixo principal (vertical)
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                spacing=10,
            ),
            width=100,  # Reduzindo o tamanho dos cards para caber melhor
            height=100,
            border_radius=15,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.WHITE,
            padding=10,
            on_click=lambda e: page.go(rota),  # Navegar para a rota específica
            shadow=ft.BoxShadow(
                blur_radius=10,
                spread_radius=2,
                color="#CCCCCC33",  # Cinza com 20% de opacidade
            ),
        )

    # Layout da tela de administração
    layout = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        controls=[
            # Título
            ft.Text(
                value="Administração do Sistema",
                size=24,
                weight="bold",
                text_align="center",
            ),
            # Grid de cards
            ft.GridView(
                expand=False,
                runs_count=2,  # Alinha os cards em duas colunas
                spacing=15,
                max_extent=120,  # Controla o tamanho máximo dos cards
                controls=[
                    criar_card("access_time", "Registrar Ponto", "/requests"),
                    criar_card("insert_chart", "Relatórios", "/requests"),
                    criar_card("group", "Funcionários", "/team"),
                    criar_card("calendar_today", "Escalas", "/escalas"),
                    criar_card("settings", "Configurações", "/configuracoes"),
                    criar_card("account_balance_wallet", "Banco de Horas", "/banco_horas"),
                    criar_card("fingerprint", "Prova de Vida", "/prova_vida"),
                    criar_card("autorenew", "Sincronizar", "/"),
                ],
            ),
            # Botão de voltar como um link azul
            ft.TextButton(
                text="Voltar",
                on_click=voltar,
                style=ft.ButtonStyle(
                    color=ft.colors.BLUE,  # Texto azul
                    padding=ft.Padding(left=10, top=5, right=10, bottom=5),  # Reduz padding
                ),
            ),
        ],
    )

    # Retorna a tela como um View
    return ft.View(route="/administracao", controls=[layout])
