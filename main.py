from os import system
from requests import get, post
from time import time
from random import choice
from urllib.parse import urlencode

system('cls || clear')

def get_kahoot(pin: str) -> tuple:
    data: dict = get(f'https://create.kahoot.it/rest/challenges/pin/{pin}').json()
    
    global_infos = []
    resp = []
    answers = []
    titles = []

    for part, infos in data.items():
        if part == 'challenge':
            for key, value in infos.items():
                if key in ['challengeId', 'hostOrganisationId', 'quizId', 'questionsCount', 'title']:
                    global_infos.append(value)

                elif key == 'quizMaster':
                    global_infos.append(dict(list(value.items())[:2]))
                    
        else:
            global_infos.append(infos['quizType'])

            for d in infos['questions']:
                titles.append(d['question'])
                answers.append(d['choices'])

                valid_resp = []
                for answer in d['choices']:
                    
                    if answer['correct']:
                        
                        valid_resp.append(answer['answer'])

                resp.append(choice(valid_resp))

    username_taken = get(f'https://create.kahoot.it/rest/challenges/{global_infos[0]}/answers').json()['challenge']["uniqueUsers"]

    return global_infos, resp, answers, username_taken, titles      

def format_anwser(username: str, player_cid: int, choices: list, titles: str, answer: str, choice_index: int, index: int, infos) -> dict:
    challenge_id, quiz_master, host_id, kahoot_id, title, quest_num, quiz_type = infos

    start = int(time())
    end = start + 1

    json_data = {
        "created": 0,
        "device": {
            "screen": {
            "height": 600,
            "width": 1066
            },
            "userAgent": "Kahoot/5.6.1.1854 (no.mobitroll.kahoot.android) (Android 9)"
        },
        "gameMode": 2,
        "gameOptions": 0,
        "hostOrganisationId": host_id,
        "modified": 0,
        "numQuestions": quest_num,
        "question": {
            "answers": [
            {
                "choiceIndex": choice_index,
                "isCorrect": True,
                "playerCid": player_cid,
                "playerId": username,
                "playerIsGhost": False,
                "points": 1000,
                "reactionTime": start - end,
                "receivedTime": end,
                "text": answer
            }
            ],
            "choices": choices,
            "duration": 20000,
            "format": 0,
            "index": index,
            "lag": 0,
            "layout": "CLASSIC",
            "playerCount": 2,
            "pointsQuestion": True,
            "skipped": False,
            "startTime": start,
            "title": titles,
            "type": quiz_type
        },
        "quizId": kahoot_id,
        "quizMaster": quiz_master,
        "quizTitle": title,
        "quizType": quiz_type,
        "quizVisibility": 0,
        "startTime": int(challenge_id.split('_')[-1])
        }

    return json_data


if __name__ == '__main__':
    valid_pin = None
    pin = input('[?] Kahoot Pin: ')

    while not valid_pin:
        try:
            infos, reponse, choices, username_taken, titles = get_kahoot(pin)
            challenge_id, title, quest_num = infos[0], infos[4], infos[5]
            
            valid_pin = True
        except:
            print('[!] Wrong Pin\n')
            pin = input('[?] Kahoot Pin: ')

    system(f'title ' + title + f' [ Total Question: 0/{quest_num} ]') 

    username = input('\n[?] Username: ')


    while username in username_taken:
        print('[!] Username is taken !')
        username = input('\n[?] Username: ')

    player_cid = post(f'https://create.kahoot.it/rest/challenges/{challenge_id}/join', params=urlencode({'nickname': username})).json()['playerCid']

    print(f'\n[!] Success: {username} | {player_cid}\n')

    print('\n\n[*] Answering Questions...')

    for i in range(len(reponse)):
        to_post = format_anwser(username, player_cid, choices[i], titles[i], reponse[i], choices[i].index({'answer': reponse[i], 'correct': True}), i, infos)
        
        res = post(f'https://create.kahoot.it/rest/challenges/{challenge_id}/answers', json=to_post)
        get(f'https://create.kahoot.it/rest/challenges/{challenge_id}/answers?modifiedTime={int(time())}')

        if res.status_code == 204:
            system(f'title ' + title + f' [ Total Question: {i + 1}/{quest_num} ~ Points: {(i + 1) * 1000} ]') 
        else:
            input(res.content)




    input('\n[!] Task completed')
