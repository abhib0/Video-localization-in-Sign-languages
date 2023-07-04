import whisper
from pytube import YouTube
import ssl
import os
import csv
import json
from moviepy.editor import VideoFileClip
from moviepy.editor import *
import spacy
import re
import string
import pyinflect
import shutil
from natsort import natsorted
from translator import translate #for translation



# youtube_video_url = "https://www.youtube.com/watch?v=RhQCxauTPp4&ab_channel=LerneDeutsch"
# youtube_video = YouTube(youtube_video_url)

# # Disable SSL certificate verification
# ssl._create_default_https_context = ssl._create_unverified_context
# streams = youtube_video.streams.filter(only_audio=True)
# stream = streams.first()
# stream.download(filename='hello.mp4')
# # do the transcription
def signVideoGenerator(file_name):
    model = whisper.load_model('base')
    # file_name=  "/Users/abhib/Desktop/untitled_folder/combined_videos/news3.mp4"
    output = model.transcribe(file_name, task= 'translate')
    print(output['text'])
    print(output['language'])

    # Extract relevant information from the JSON data
    segments = output['segments']
    output_rows = []
    for segment in segments:
        row = {
            'id': segment['id'],
            'sentence': segment['text'],
            'start_time': segment['start'],
            'end_time': segment['end']
        }
        output_rows.append(row)

    # Write the extracted data to a CSV file
    csv_file = '/Users/abhib/Desktop/untitled_folder/data.csv'
    fieldnames = ['id', 'sentence', 'start_time', 'end_time']
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"CSV file '{csv_file}' has been generated successfully.")

    # for text to gloss function
    # Rules for finding tense in a given sentence
    rules = {
        'Present_Simple': lambda token: token.tag_ in ['VBP', 'VBZ'] and token.dep_ == 'ROOT',
        'Present_Continuous': lambda token: re.search(r'be', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBG' and token.text in ["'m", "'re", "'s", "am", "are", "is"] and not 'have' in [i.lemma_ for i in token.head.children] and not 'xcomp' in [i.dep_ for i in token.head.children],
        'Present_Perfect': lambda token: re.search(r'have', token.lemma_) and token.dep_ == 'aux' and not token.head.text == 'got' and token.head.tag_ == 'VBN' and not re.search(r'd', token.text) and not re.search(r'(\'d|would|might|may|could)', str([i.lemma_ for i in token.head.children])),
        'Present_Perfect_Continuous': lambda token: re.search(r'have', token.lemma_) and token.dep_ == 'aux' and not token.head.text == 'got' and token.head.tag_ == 'VBG' and not re.search(r'd', token.text),
        'Past_Simple': lambda token: token.tag_ == 'VBD' and token.dep_ == 'ROOT' or token.text in ['Did', 'did'],
        'Past_Continuous': lambda token: re.search(r'be', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBG' and token.text in ['were', 'was'] and not 'have' in [i.lemma_ for i in token.head.children] and not 'xcomp' in [i.dep_ for i in token.head.children],
        'Past_Perfect': lambda token: re.search(r'have', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBN' and not re.search(r'(s|v)', token.text),
        'Past_Perfect_Continuous': lambda token: re.search(r'have', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBG' and not re.search(r'(s|v)', token.text),
        'Future_Simple': lambda token: token.tag_ == 'MD' and token.dep_ == 'aux' and token.head.tag_ == 'VB',
        'Future_Continuous': lambda token: re.search(r'will', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBG' and not 'have' in [i.text for i in token.head.children] and not 'xcomp' in [i.dep_ for i in token.head.children],
        'Future_Perfect': lambda token: re.search(r'will', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBN' and 'have' in [i.text for i in token.head.children] and not 'xcomp' in [i.dep_ for i in token.head.children],
        'Future_Perfect_Continuous': lambda token: re.search(r'will', token.lemma_) and token.dep_ == 'aux' and token.head.tag_ == 'VBG' and 'have' in [i.text for i in token.head.children]
    }
    nlp = spacy.load("en_core_web_sm")

    def lemmatize_sentence(sentence):
        doc = nlp(sentence)
        lemmatized_tokens = []
        for token in doc:
            if token.text.lower() in ["is", "am", "are", "was", "were"]:
                lemmatized_tokens.append(token.text)
            elif token.lemma_ == "-PRON-":
                lemmatized_tokens.append(token.text.lower())  # Use lowercase pronoun
            else:
                lemmatized_tokens.append(token.lemma_)
        lemmatized_sentence = " ".join(lemmatized_tokens)
        return lemmatized_sentence

    def remove_unwanted(sentence):
        verb_list = ["is", "am", "are", "was", "were","be"]
        words = sentence.split()
        filtered_words = [word for word in words if word.lower() not in verb_list]
        result = " ".join(filtered_words)
        # Create a translation table with punctuation characters mapped to None
        translator = str.maketrans("", "", string.punctuation)
        # Remove punctuation using translate() method
        result = result.translate(translator)
        return result

    def insert_spaces(sentence):
        # Use regular expression to find numeric values
        pattern = r'\d+'
        matches = re.findall(pattern, sentence)
        # Iterate over the matches and insert spaces
        for match in matches:
            sentence = sentence.replace(match, ' '.join(match))
        return sentence

    def get_tense(sentence):
        doc = nlp(sentence)
        for token in doc:
            for tense, rule in rules.items():
                if rule(token):
                    return tense
        return "Unknown"

    # simple past --> BEFORE + simple present
    def function1(input_sentence):
        doc_dep = nlp(input_sentence)
        for i in range(len(doc_dep)):
            token = doc_dep[i]
            if token.tag_ == "VBD":
                inflected_form = token._.inflect("VBP")
                if inflected_form:
                    input_sentence = input_sentence.replace(token.text, inflected_form)
        input_sentence = "BEFORE " + " ".join([word for word in input_sentence.split() if word not in ["is", "am", "are", "be"]])
        return input_sentence

    def function2(input_sentence):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(input_sentence)
        output_tokens = []
        input_tense = get_tense(input_sentence)
        
        for token in doc:
            if token.pos_ == "VERB":
                if token.tag_ == "VBG" and token.dep_ == "ROOT":
                    output_tokens.append(token.lemma_)
                else:
                    output_tokens.append(token.text)
            elif token.dep_ == "aux" and token.head.pos_ == "VERB" and token.head.tag_ == "VBG":
                continue
            else:
                output_tokens.append(token.text)
        
        output_sentence = " ".join(output_tokens)
        
        if input_tense == "Past_Continuous" :
            output_sentence = "BEFORE " + output_sentence
        elif input_tense == "Present_Continuous":
            output_sentence = "NOW " + output_sentence
        
        return output_sentence


    def function3(input_sentence):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(input_sentence)
        output_tokens = []
        
        for token in doc:
            if token.pos_ == "VERB":
                if token.tag_ == "VBN" and token.dep_ == "ROOT":
                    output_tokens.append(token.lemma_)
                else:
                    output_tokens.append(token.text)
            elif token.dep_ == "aux" and token.head.pos_ == "VERB" and token.head.tag_ == "VBN":
                continue
            else:
                output_tokens.append(token.text)
        
        output_sentence = " ".join(output_tokens)
        
        return output_sentence

    def function4(input_sentence):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(input_sentence)
        
        output_tokens = []
        
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ == "ROOT":
                if token.tag_ == "VBG":
                    output_tokens.append(token.lemma_)
                else:
                    output_tokens.append(token.text)
            elif token.dep_ == "aux" and token.text in ["be", "been", "have"]:
                continue
            else:
                output_tokens.append(token.text)
        
        output_sentence = " ".join(output_tokens)
        return "NEXT " + output_sentence

    def function5(sentence):
        doc = nlp(sentence)
        input_tense = get_tense(sentence)

        output_tokens = []
        
        for token in doc:
            if token.pos_ == "VERB":
                if token.tag_ == "VBG" and token.dep_ == "ROOT":
                    output_tokens.append("have")
                    output_tokens.append(token.lemma_)
                else:
                    output_tokens.append(token.text)
            elif token.dep_ == "aux" and token.head.pos_ == "VERB" and token.head.tag_ == "VBG":
                continue
            else:
                output_tokens.append(token.text)

        output_sentence = " ".join(output_tokens)
        if input_tense == "Past_Perfect_Continuous":
            output_sentence = "BEFORE " + output_sentence
        elif input_tense == "Present_Perfect_Continuous":
            output_sentence = "NOW " + output_sentence
        return output_sentence

    def func(input_sentence, input_tense):
        if input_tense == "Past_Simple":
            output_sentence = function1(input_sentence)
        elif input_tense == "Past_Continuous" or input_tense == "Present_Continuous":
            output_sentence = function2(input_sentence)
        elif input_tense == "Future_Simple":
            output_sentence = function3(input_sentence)
        elif input_tense == "Future_Continuous" or input_tense == "Future_Perfect_Continuous":
            output_sentence = function4(input_sentence)
        elif input_tense == "Simple_Present" or input_tense == "Unknown":
            output_sentence = input_sentence
        elif input_tense == "Past_Perfect_Continuous" or input_tense == "Present_Perfect_Continuous":
            output_sentence = function5(input_sentence)
        else:
            output_sentence = input_sentence
        
        sen1= lemmatize_sentence(output_sentence)
        sen2= remove_unwanted(sen1)
        sen3= insert_spaces(sen2)
        return sen3

    #for gloss to video function
    folder6 = "/Users/abhib/Desktop/untitled_folder/folder6"
    folder7 = "/Users/abhib/Desktop/untitled_folder/folder7"
    folder8 = "/Users/abhib/Desktop/untitled_folder/folder8"
    folder9 = "/Users/abhib/Desktop/untitled_folder/folder9"
    dataset_folder= "/Users/abhib/Desktop/untitled_folder/german_signs"


    # Function to search for word.mp4 files in the specified dataset folder
    def search_word_in_dataset(word):
        print("searching for: "+ word)
        file_names = os.listdir(dataset_folder)
        for file_name in file_names:
            if file_name == word + ".mp4":
                return os.path.join(dataset_folder, file_name)
        for file_name in file_names:
            if word in file_name.split("_"):
                return os.path.join(dataset_folder, file_name)    
        return None


    # Function to process each word in a sentence
    def process_word(word, folder6):
        video_found = False
        count = len(os.listdir(folder6))

        # Search for the word in the dataset
        dataset_path = search_word_in_dataset(word)
        if dataset_path:
                # Copy the video to folder6 with the assigned count number
                video_filename = f"{count}.mp4"
                output_filepath = os.path.join(folder6, video_filename)
                shutil.copyfile(dataset_path, output_filepath)
                video_found = True

        # If word is not found, perform finger spelling
        if not video_found:
            # Split the word into letters
            letters = list(word)
            # if len(letters)> 4 :
            #     return
            # Process each letter individually
            for letter in letters:
                letter_path = search_word_in_dataset(letter)
                count = len(os.listdir(folder6))
                if letter_path:
                    # Copy the letter video to folder6 with the assigned count number
                    video_filename = f"{count}.mp4"
                    output_filepath = os.path.join(folder6, video_filename)
                    shutil.copyfile(letter_path, output_filepath)    
                else:
                    print(f"Letter video not found for letter '{letter}'")                 

    # Function to combine videos in folder6 and save the combined video in folder7
    def combine_videos(folder6, folder7):
        # Get a list of video files in folder6
        video_files = os.listdir(folder6)

        # Filter only the video files (e.g., with .mp4 extension)
        video_files = [file for file in video_files if file.endswith('.mp4')]

        # Sort the video files using natural sorting
        video_files = natsorted(video_files)
        print(video_files)
        #Concatenate videos in the order of their arrival
        clips = []
        for file in video_files:
            video_path = os.path.join(folder6, file)  # Provide the full path of the video file
            clip = VideoFileClip(video_path)
            clips.append(clip)
        if len(clips) == 0:
            return  
        final_clip = concatenate_videoclips(clips)

        # Save the combined video in folder7
        p = len(os.listdir(folder7))
        video_filename = f"{p}.mp4"
        output_filepath = os.path.join(folder7, video_filename)
        final_clip.write_videofile(output_filepath)

        # Delete all videos in folder6
        for file in video_files:
            video_path = os.path.join(folder6, file)  
            os.remove(video_path)

    def change_video_speed(file_path,output_path, start_time, end_time):
        # Load the video clip
        clip = VideoFileClip(file_path)
        # Get the original duration of the clip
        original_duration = clip.duration
        # target_duration = end_time - start_time
        # factor = original_duration/target_duration
        # Change the speed of the clip while preserving the target duration
        # if target_duration < 7 and original_duration > 60 :
        #     target_duration = 7
        new_clip = clip.speedx(4)

        # Save the new video clip with the desired speed
        new_clip.write_videofile(output_path)
        # Close the clips
        clip.close()
        new_clip.close()

    def batch_change_video_speed(folder7, folder8, start_time, end_time, segment_id):
    # Construct the file name for the specific segment_id
        file_name = f"{segment_id}.mp4"
        file_path = os.path.join(folder7, file_name)
        
        # Check if the file exists in folder7
        if os.path.exists(file_path):
            # Generate the output file path in folder8 with the same file name
            output_path = os.path.join(folder8, file_name)
            # Change the video speed using the change_video_speed function
            change_video_speed(file_path, output_path, start_time, end_time)
        else:
            return 
            


    def normalize_german_word(word):
        replacements = {'ß': 'ss', 'ä': 'a', 'ö': 'o', 'ü': 'u'}
        symbols_to_remove = ['«', '»', '–', '—', '…']

        for symbol, replacement in replacements.items():
            word = word.replace(symbol, replacement)

        for symbol in symbols_to_remove:
            word = word.replace(symbol, '')

        return word 
        
    def process_gloss(gloss, folder6, folder7):
        # Process each sentence
        # Remove all punctuations from the sentence
        sentence = gloss.translate(str.maketrans('', '', string.punctuation))
        # Split sentence into words
        words = sentence.split()
        # Process each word
        for word in words:
            word= word.lower() #word is in english
            print(word + "---")
            #translate the word from english to german
            translate(word) #json file formed
            # from file.json, extract text
            # Read JSON file
            with open('file.json') as json_file:
                json_data = json.load(json_file)

            # Extract text
            word = json_data[0]['translations'][0]['text']
            word= word.lower()
            word = normalize_german_word(word)
            print(word)
            process_word(word, folder6)
        # Combine videos in folder6 and deleting all videos from folder6 after combining
        combine_videos(folder6, folder7)
        
        
            
    # Function to convert text to gloss using the locally stored code
    def text_to_gloss(text):
        input_tense = get_tense(text)
        output_sentence = func(text, input_tense)
        print(output_sentence)
        return output_sentence
        

    # Function to generate video from gloss using the locally stored code and datasets
    def gloss_to_video(gloss):
        process_gloss (gloss, folder6, folder7)


    # Iterate over each row in the CSV file
    def process_csv_file(csv_file):
        with open(csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                segment_id = row['id']
                text = row['sentence']
                start_time = float(row['start_time'])
                end_time = float(row['end_time'])
            
                # Convert text to gloss
                gloss = text_to_gloss(text)
                
                # Generate video from gloss
                gloss_to_video(gloss) 
                
                #folder7 has all the sentence videos
                batch_change_video_speed(folder7, folder8, start_time, end_time, segment_id)
            
            # Delete all videos in folder7
            for file in os.listdir(folder7):
                file_path = os.path.join(folder7, file)
                os.remove(file_path)
            #folder8 has all the sentence videos (in sync)
            combine_videos(folder8, folder9)
            #folder9 has the sign video for the whole input video transcription

    # Specify the path to the CSV file
    csv_file = '/Users/abhib/Desktop/untitled_folder/data.csv'

    # Process the CSV file
    process_csv_file(csv_file)







