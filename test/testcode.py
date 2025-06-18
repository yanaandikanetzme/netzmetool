import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def solve_sudoku(board):
    empty = find_empty(board)
    if not empty:
        return True
    row, col = empty

    for num in range(1, 10):
        if is_valid(board, num, (row, col)):
            board[row][col] = num

            if solve_sudoku(board):
                return True

            board[row][col] = 0

    return False

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def is_valid(board, num, pos):
    for i in range(9):
        if board[pos[0]][i] == num and pos[1] != i:
            return False

    for i in range(9):
        if board[i][pos[1]] == num and pos[0] != i:
            return False

    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num and (i, j) != pos:
                return False

    return True

def solve():
    board = [[0 for _ in range(9)] for _ in range(9)]
    for i in range(9):
        for j in range(9):
            val = entries[i][j].get()
            if val.isdigit() and 1 <= int(val) <= 9:
                board[i][j] = int(val)
            elif val:
                messagebox.showerror("Error", "Invalid input. Please enter numbers 1-9 only.")
                return

    if solve_sudoku(board):
        for i in range(9):
            for j in range(9):
                entries[i][j].delete(0, tk.END)
                entries[i][j].insert(0, str(board[i][j]))
                entries[i][j].config(state='readonly')
        global is_solved
        is_solved = True
    else:
        messagebox.showerror("Error", "No solution exists for this Sudoku puzzle.")

def reset():
    global is_solved
    is_solved = False
    for i in range(9):
        for j in range(9):
            entries[i][j].config(state='normal', bg='white', fg='black')
            entries[i][j].delete(0, tk.END)

def highlight_number(event):
    if is_solved:
        widget = event.widget
        value = widget.get()
        if value:
            for i in range(9):
                for j in range(9):
                    if entries[i][j].get() == value:
                        entries[i][j].config(bg='yellow')
                    else:
                        entries[i][j].config(bg='white')

root = tk.Tk()
root.title("Sudoku Solver")

is_solved = False

# Membuat frame utama
main_frame = tk.Frame(root, bd=2, relief=tk.RAISED)
main_frame.pack(padx=10, pady=10)

entries = [[None for _ in range(9)] for _ in range(9)]
for block_i in range(3):
    for block_j in range(3):
        block_frame = tk.Frame(main_frame, bd=2, relief=tk.RAISED)
        block_frame.grid(row=block_i, column=block_j, padx=2, pady=2)
        
        for i in range(3):
            for j in range(3):
                e = tk.Entry(block_frame, width=2, font=('Arial', 18), justify='center')
                e.grid(row=i, column=j, padx=1, pady=1, ipady=5)
                e.bind('<Button-1>', highlight_number)
                entries[block_i*3 + i][block_j*3 + j] = e

# Frame untuk tombol
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

solve_button = ttk.Button(button_frame, text="Solve", command=solve)
solve_button.pack(side=tk.LEFT, padx=5)

reset_button = ttk.Button(button_frame, text="Reset", command=reset)
reset_button.pack(side=tk.LEFT, padx=5)

root.mainloop()