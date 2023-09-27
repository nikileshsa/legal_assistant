import re
import openai
from time import time, sleep
from halo import Halo
import textwrap
import yaml


###     file operations


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


###     API functions


def chatbot(conversation, model="gpt-4-0613", temperature=0, max_tokens=2000):
    max_retry = 7
    retry = 0
    while True:
        try:
            spinner = Halo(text='Thinking...', spinner='dots')
            spinner.start()
            
            response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
            text = response['choices'][0]['message']['content']

            spinner.stop()
            
            return text, response['usage']['total_tokens']
        except Exception as oops:
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            exit(5)


def chat_print(text):
    formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in text.split('\n')]
    formatted_text = '\n'.join(formatted_lines)
    print('\n\n\nCHATBOT:\n\n%s' % formatted_text)


if __name__ == '__main__':
    openai.api_key = open_file('key_openai.txt').strip()
    
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_01_intake.md')})
    user_messages = list()
    all_messages = list()
    print('Describe your legal issue to the intake bot. Type DONE when done.')
    
    ## INTAKE PORTION
    
    while True:
        # get user input
        text = input('\n\nCLIENT: ').strip()
        if text == 'DONE':
            break
        user_messages.append(text)
        all_messages.append('CLIENT: %s' % text)
        conversation.append({'role': 'user', 'content': text})
        response, tokens = chatbot(conversation)
        conversation.append({'role': 'assistant', 'content': response})
        all_messages.append('INTAKE: %s' % response)
        print('\n\nINTAKE: %s' % response)
    
    ## CHARTING NOTES
    
    print('\n\nGenerating Intake Notes')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_02_prepare_notes.md')})
    text_block = '\n\n'.join(all_messages)
    chat_log = '<<BEGIN LEGAL INTAKE CHAT>>\n\n%s\n\n<<END LEGAL INTAKE CHAT>>' % text_block
    save_file('logs/log_%s_chat.txt' % time(), chat_log)
    conversation.append({'role': 'user', 'content': chat_log})
    notes, tokens = chatbot(conversation)
    print('\n\nNotes version of conversation:\n\n%s' % notes)
    save_file('logs/log_%s_notes.txt' % time(), notes)
    
    ## GENERATING REPORT

    print('\n\nGenerating Legal Hypothesis Report')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_03_evaluation.md')})
    conversation.append({'role': 'user', 'content': notes})
    report, tokens = chatbot(conversation)
    save_file('logs/log_%s_evaluation.txt' % time(), report)
    print('\n\nHypothesis Report:\n\n%s' % report)

    ## LEGAL EVALUATION

    print('\n\nPreparing for Legal Evaluation')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_04_forensic.md')})
    conversation.append({'role': 'user', 'content': notes})
    clinical, tokens = chatbot(conversation)
    save_file('logs/log_%s_forensic.txt' % time(), clinical)
    print('\n\nClinical Evaluation:\n\n%s' % clinical)

    ## REFERRALS

    print('\n\nGenerating Referrals')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_05_recommendations.md')})
    conversation.append({'role': 'user', 'content': notes})
    referrals, tokens = chatbot(conversation)
    save_file('logs/log_%s_recommendations.txt' % time(), referrals)
    print('\n\nReferrals and Tests:\n\n%s' % referrals)

    ## DOCUMENTS GENERATION

    print('\n\nGenerating Documents')
    conversation = list()
    conversation.append({'role': 'system', 'content': open_file('system_06_documentpreparation.md')})
    conversation.append({'role': 'user', 'content': notes})
    documents, tokens = chatbot(conversation)
    save_file('logs/log_%s_documentprepare.txt' % time(), documents)
    print('\n\nDocumentation for case:\n\n%s' % documents)
