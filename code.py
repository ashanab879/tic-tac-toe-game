import random 
import asyncio 

from flet import ( 
    Page,
    AppBar,
    Text,
    Container, 
    MainAxisAlignment,
    TextAlign,
    Colors,
    Row,
    Column,
    FontWeight,
    app,
    border_radius,
    alignment,
    border,
)


GAME_MODE = None 

player_x_turn = True 
board = [""] * 9 
board_buttons = []

score = {
    "X": 0,
    "O": 0,
    "Draws": 0
}


status_text = Text("X's turn", size=24, weight=FontWeight.BOLD, color=Colors.BLACK)
score_x_text = Text(f"X Wins: {score['X']}", size=16, weight=FontWeight.BOLD, color=Colors.RED_700)
score_o_text = Text(f"O Wins: {score['O']}", size=16, weight=FontWeight.BOLD, color=Colors.BLUE_700)
score_draws_text = Text(f"Draws: {score['Draws']}", size=16, color=Colors.BLACK54)


main_content = Column(
    [],
    horizontal_alignment="center",
    alignment=MainAxisAlignment.START, 
    scroll="auto" 
)


async def main(page: Page):
    page.title = "لعبة إكس أو (X O) - Flet"
    page.bgcolor = Colors.GREY_100 
    page.vertical_alignment = MainAxisAlignment.START 
    page.horizontal_alignment = "center"
    page.theme_mode = "light"
  
    global player_x_turn, board, status_text, board_buttons, score, score_x_text, score_o_text, score_draws_text, GAME_MODE, main_content

 
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]

    def update_score_display():
        score_x_text.value = f"X Wins: {score['X']}"
        score_o_text.value = f"O Wins: {score['O']}"
        score_draws_text.value = f"Draws: {score['Draws']}"
        page.update()

    def check_for_winner():
        for combo in winning_combinations:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] and board[combo[0]] != "":
                winner = board[combo[0]]
                
                score[winner] += 1
                update_score_display()
                
                status_text.value = f"Winner: {winner}!"
                status_text.color = Colors.RED_500 if winner == "X" else Colors.BLUE_500
                
                for cell in board_buttons:
                    cell.on_click = None 

                for i in combo:
                    board_buttons[i].bgcolor = Colors.AMBER_100
                    
                page.update()
                return True
        
        if "" not in board:
           
            score['Draws'] += 1
            update_score_display()
            
            status_text.value = "Draw! 🤝"
            status_text.color = Colors.ORANGE_500
            
            for cell in board_buttons:
                cell.on_click = None 
                
            page.update()
            return True
            
        return False

   
    def get_empty_cells():
        return [i for i, cell in enumerate(board) if cell == ""]

    def find_best_move(player):
        for combo in winning_combinations:
            cells_in_combo = [board[i] for i in combo]
            
            if cells_in_combo.count(player) == 2 and cells_in_combo.count("") == 1:
                for index in combo:
                    if board[index] == "":
                        return index
        return None

    def computer_move():
        global player_x_turn
        
        if status_text.value.startswith(("Winner", "Draw")):
            return

        empty_cells = get_empty_cells()
        
        if not empty_cells:
            return 
            
        best_move = None
        
        best_move = find_best_move("O")
        
        if best_move is None:
            best_move = find_best_move("X") 
        
        if best_move is None:
            if 4 in empty_cells: 
                 best_move = 4
            else:
                best_move = random.choice(empty_cells)
        
        
        index = best_move
        symbol = "O"
        
        board[index] = symbol
        
        board_buttons[index].content = Text(
            symbol,
            size=36, 
            weight=FontWeight.BOLD,
            color=Colors.BLUE_500,
            text_align=TextAlign.CENTER
        )
        board_buttons[index].on_click = None 

        if not check_for_winner():
            player_x_turn = True 
            status_text.value = "X's turn"
            status_text.color = Colors.RED_700
            
        
        page.update()

    async def handle_click(e):
        global player_x_turn, GAME_MODE
        
        if status_text.value.startswith(("Winner", "Draw")) or (GAME_MODE == 'AI' and not player_x_turn):
            return
            
        index = e.control.data
        
        if board[index] == "":
            
            symbol = "X" if player_x_turn else "O"
            board[index] = symbol
            
            e.control.content = Text(
                symbol,
                size=36, 
                weight=FontWeight.BOLD,
                color=Colors.RED_500 if symbol == "X" else Colors.BLUE_500,
                text_align=TextAlign.CENTER
            )
            
            e.control.update() 
            
            if not check_for_winner():
                
                if GAME_MODE == 'FRIEND':
                    player_x_turn = not player_x_turn
                    next_player = "X" if player_x_turn else "O"
                    status_text.value = f"{next_player}'s turn"
                    status_text.color = Colors.RED_700 if player_x_turn else Colors.BLUE_700
                    page.update()
                    
                elif GAME_MODE == 'AI':
                    player_x_turn = False 
                    status_text.value = f"O's turn (Computer)"
                    status_text.color = Colors.BLUE_700
                    page.update()
                    
                    await asyncio.sleep(0.5) 
                    computer_move()
            
    def restart_game(e):
        global player_x_turn, board
        
        player_x_turn = True
        board = [""] * 9
        
        
        status_text.value = "X's turn"
        status_text.color = Colors.BLACK
        
        for cell in board_buttons:
            cell.content = Text("") 
            cell.bgcolor = Colors.GREY_50 
            cell.border = border.all(3, Colors.BLUE_GREY_400)
            cell.on_click = handle_click 
            
        page.update()


    scoreboard = Row(
        [
            Container(content=score_x_text, padding=10, border_radius=5, bgcolor=Colors.RED_50),
            Container(content=score_draws_text, padding=10, border_radius=5, bgcolor=Colors.GREY_200),
            Container(content=score_o_text, padding=10, border_radius=5, bgcolor=Colors.BLUE_50),
        ],
        spacing=15,
        alignment=MainAxisAlignment.CENTER,
    )
    
    if not board_buttons:
        for i in range(9):
            cell = Container(
                content=Text(""), 
                width=80,  
                height=80, 
                on_click=handle_click, 
                data=i, 
                bgcolor=Colors.GREY_50, 
                border_radius=10, 
                border=border.all(3, Colors.BLUE_GREY_400), 
                alignment=alignment.center, 
            )
            board_buttons.append(cell)
            
    board_layout = Column(
        [
            Row(board_buttons[0:3], spacing=3, alignment=MainAxisAlignment.CENTER), 
            Row(board_buttons[3:6], spacing=3, alignment=MainAxisAlignment.CENTER),
            Row(board_buttons[6:9], spacing=3, alignment=MainAxisAlignment.CENTER),
        ],
        spacing=3, 
        alignment=MainAxisAlignment.CENTER,
    )
    
    game_board_container = Container(
        content=board_layout,
        padding=10,
        bgcolor=Colors.WHITE,
        border_radius=15,
        alignment=alignment.center,
        width=300,  
        height=300, 
    )
    
    restart_button = Container(
        content=Text("Restart Game", color=Colors.WHITE, weight=FontWeight.BOLD),
        on_click=restart_game,
        height=40, 
        width=150, 
        bgcolor=Colors.GREEN_600,
        border_radius=8,
        alignment=alignment.center,
    )
    
    back_button = Container(
        content=Text("Main Menu", color=Colors.WHITE, weight=FontWeight.BOLD),
        on_click=lambda e: show_main_menu(),
        height=40, 
        width=150, 
        bgcolor=Colors.BLUE_GREY_400,
        border_radius=8,
        alignment=alignment.center,
    )
    
    game_screen_controls = Column(
        [
            Container(height=10), 
            scoreboard, 
            Container(height=15),
            status_text, 
            Container(height=15),
            game_board_container, 
            Container(height=30), 
            Row([restart_button, back_button], spacing=10, alignment=MainAxisAlignment.CENTER),
            Container(height=10) 
        ],
        horizontal_alignment="center",
        alignment=MainAxisAlignment.START, 
        scroll="auto" 
    )

    
    def start_game(mode):
        global GAME_MODE
        GAME_MODE = mode
        
        restart_game(None) 
        
        main_content.controls.clear()
        main_content.controls.append(game_screen_controls)
        page.update()
        
    def create_menu_button(text, on_click_func):
        return Container(
            content=Row(
                [
                    Text(text, color=Colors.WHITE, size=20, weight=FontWeight.BOLD)
                ],
                alignment=MainAxisAlignment.CENTER, 
                spacing=10
            ),
            width=250,
            height=60,
            margin=10,
            padding=10,
            bgcolor=Colors.BLUE_GREY_700,
            border_radius=10,
            on_click=on_click_func,
            alignment=alignment.center
        )

    def show_main_menu():
        global GAME_MODE
        GAME_MODE = None
        
        main_content.controls.clear()
        main_content.controls.append(
            Column(
                [
                    Text("اختر وضع اللعب", size=30, weight=FontWeight.BOLD, color=Colors.BLACK),
                    Container(height=30),
                    create_menu_button(
                        "ضد الكمبيوتر (AI)", 
                        lambda e: start_game('AI')
                    ),
                    create_menu_button(
                        "ضد صديق (2 Player)", 
                        lambda e: start_game('FRIEND')
                    ),
                ],
                horizontal_alignment="center",
                alignment=MainAxisAlignment.CENTER,
                expand=True
            )
        )
        page.update()


    appbar = AppBar(
        bgcolor=Colors.BLUE_GREY_900,
        title=Text("لعبة إكس أو (X O)", color=Colors.WHITE, weight=FontWeight.BOLD),
        center_title=True,
    )
    
    page.add(
        appbar,
        Container(
            content=main_content,
            expand=True 
        )
    )

    show_main_menu()


app(target=main)
