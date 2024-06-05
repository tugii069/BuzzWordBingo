import random
import os
import time
import json
from multiprocessing import Process, Queue

def generate_bingo_card(words, xaxis, yaxis):
    if len(words) < xaxis * yaxis:
        raise ValueError("Not enough words in the word list to fill the bingo card.")
    random.shuffle(words)
    card = []
    for i in range(yaxis):
        row = words[i * xaxis:(i + 1) * xaxis]
        card.append(row)
    return card

def display_card(card):
    for row in card:
        print(" | ".join(row))
        print("-" * (len(row) * 4))

def check_winner(card):
    # Check rows
    for row in card:
        if all(cell == 'X' for cell in row):
            return True
    # Check columns
    #Check
    for col in range(len(card[0])):
        if all(row[col] == 'X' for row in card):
            return True
    # Check diagonals
    if all(card[i][i] == 'X' for i in range(len(card))):
        return True
    if all(card[i][len(card)-1-i] == 'X' for i in range(len(card))):
        return True
    return False

def play_bingo(player_name, card, queue):
    while True:
        print(f"\n{player_name}'s Bingo Card:")
        display_card(card)
        message = json.loads(queue.get())
        if message['type'] == 'WORD':
            word = message['data']
            print(f"{player_name} received word: {word}")
            for i in range(len(card)):
                for j in range(len(card[i])):
                    if card[i][j] == word:
                        card[i][j] = 'X'
            if check_winner(card):
                print(f"\n{player_name} wins!")
                queue.put(json.dumps({'type': 'WINNER', 'data': player_name}))
                return
        elif message['type'] == 'END':
            return

def main():
    words_file = input("Enter the path to the words file: ")
    with open(words_file, 'r') as f:
        words = f.read().splitlines()

    xaxis = int(input("Enter the number of columns: "))
    yaxis = int(input("Enter the number of rows: "))

    if len(words) < xaxis * yaxis:
        print("Error: Not enough words in the word list to fill the bingo card.")
        return

    player_names = input("Enter player names separated by commas: ").split(',')

    queue = Queue()

    cards = []
    for player in player_names:
        card = generate_bingo_card(words.copy(), xaxis, yaxis)
        cards.append((player.strip(), card))

    processes = []
    for player, card in cards:
        p = Process(target=play_bingo, args=(player, card, queue))
        p.start()
        processes.append(p)

    while True:
        word = input("Enter a buzzword: ")
        queue.put(json.dumps({'type': 'WORD', 'data': word}))
        time.sleep(1)
        if not queue.empty():
            message = json.loads(queue.get())
            if message['type'] == 'WINNER':
                print(f"{message['data']} wins!")
                break

    for p in processes:
        queue.put(json.dumps({'type': 'END', 'data': None}))
        p.join()

if __name__ == "__main__":
    main()
