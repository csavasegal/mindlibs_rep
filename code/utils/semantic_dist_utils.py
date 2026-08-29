import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import string
from itertools import chain, repeat, islice
from os.path import exists
import difflib
from joblib import Parallel, delayed
import torch
import torch.nn.functional as F



# Third-party imports

import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel

# Configuration constants
BERT_MODEL = "bert-base-uncased"
FILTER_TOKENS = ['[CLS]', '[SEP]', '[UNK]', '[MASK]']

def get_bert_model(model_name='sentence-transformers/all-MiniLM-L6-v2', cache_dir=None):
    '''
    Use a model from the sentence-transformers library to get
    sentence embeddings. Models used are trained on a next-sentence
    prediction task and evaluate the likelihood of S2 following S1.
    '''
    # set the path of where to download models
    # this NEEDS to be run before loading from transformers
    if cache_dir:
        os.environ['TRANSFORMERS_CACHE'] = cache_dir

    # Load model from HuggingFace Hub
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    model = AutoModel.from_pretrained(model_name)
    
    return tokenizer, model

def deal_with_int(val):
    ''' This function (as named) deals with converted strings to integers'''
    if type(val)==str:
        val = int(val)
    elif type(val)==float:
        val = np.nan
    else:
        print('error!')
        
    return val


def get_data(trial):
    
    ''' This differs by condition (number of rows), so that is why the code is set-up this way (totally not ideal)'''
    ''' This gets the information for each trial'''
    condition = int(list(trial['condition'])[2])
    SML = trial[trial['self_ML_pure'].notnull()]['self_ML_pure'].values[0]
    #want RT of the SML trial
    RT_SML = trial[trial['self_ML_pure'].notnull()]['rt'].values[0]
    ML1 = trial[trial['self_ML_pure'].notnull()]['ML1'].values[0]
    ML2 = trial[trial['self_ML_pure'].notnull()]['ML2'].values[0]
    ML3 = trial[trial['self_ML_pure'].notnull()]['ML3'].values[0]

    input1 = trial[trial['input1'].notnull()]['input1'].values[0]
    input2 = trial[trial['input2'].notnull()]['input2'].values[0]
    input3 = trial[trial['input3'].notnull()]['input3'].values[0]
    img = trial[trial['input3'].notnull()]['img'].values[0]
    OML = trial[trial['other_ML_pure'].notnull()]['other_ML_pure'].values[0]
    other_input1 = trial[trial['other_input1'].notnull()]['other_input1'].values[0]
    other_input2 = trial[trial['other_input2'].notnull()]['other_input2'].values[0]
    other_input3 = trial[trial['other_input3'].notnull()]['other_input3'].values[0]
    

    if list(trial[trial['trial_type'] == 'image-slider-response']['side_presented_1'])[0]=='SELF':
        appraisal_SELF = int(trial[trial['trial_type'] == 'image-slider-response']['response1'])
    if list(trial[trial['trial_type'] == 'image-slider-response']['side_presented_1'])[0]=='OTHER':
        appraisal_OTHER = int(trial[trial['trial_type'] == 'image-slider-response']['response1'])
    if list(trial[trial['trial_type'] == 'image-slider-response']['side_presented_2'])[0]=='OTHER':
        appraisal_OTHER = int(trial[trial['trial_type'] == 'image-slider-response']['response2'])
    if list(trial[trial['trial_type'] == 'image-slider-response']['side_presented_2'])[0]=='SELF':
        appraisal_SELF = int(trial[trial['trial_type'] == 'image-slider-response']['response2'])

    appraisal_side_1 = list(trial[trial['trial_type'] == 'image-slider-response']['side_presented_1'])[0]
    appraisal_side_2 = list(trial[trial['trial_type'] == 'image-slider-response']['side_presented_2'])[0]
    slider_start_1 = int(trial[trial['trial_type'] == 'image-slider-response']['slider_start_1'])
    slider_start_2 = int(trial[trial['trial_type'] == 'image-slider-response']['slider_start_2'])
    slider_rt = int(trial[trial['trial_type'] == 'image-slider-response']['rt'])


    return condition, SML, RT_SML, ML1, ML2, ML3, input1, input2, input3, img, OML, other_input1,other_input2, other_input3, appraisal_SELF, appraisal_OTHER, appraisal_side_1, appraisal_side_2, slider_start_1, slider_start_2, slider_rt



def diff_between_ML_inputs(text1_lines,text2_lines):
    diff = difflib.unified_diff(text1_lines, text2_lines)
    n = 0
    result = ''
    for difference in diff:
        n += 1
        if n < 7: # the first 7 lines is a bunch of information unnecessary for waht you want
            continue
        result += difference[1] # the character at this point will either be " x", "-x" or "+x"
    return result



def BERT_using_context(batch,model_type):
    
    ''' BERT that uses the context of the previous part of the sentence (recommended by Tommy)'''
    ''' model_type can be bert or roberta'''
    
    if model_type=='bert':
    
        tokens = tokenizer(batch, padding=True, return_tensors="pt")
        embeddings = bert(**tokens)

        detokenized = [tokenizer.convert_ids_to_tokens(tk) for tk in tokens['input_ids']]
    elif model_type=='roberta':
        tokens = tokenizer_Rob(batch, padding=True, return_tensors="pt")
        try:
            embeddings = roberta(**tokens)
            detokenized = [tokenizer_Rob.convert_ids_to_tokens(tk) for tk in tokens['input_ids']]
        except:
            warnings.warn(f"Warning... was not able to work with {batch}")
            embeddings = np.nan
            detokenized = np.nan
    else:
        raise Exception('Missing model type!')
    
    return embeddings,detokenized


def avg_embeddings(tensor):
    emb_input_mean = np.mean(tensor.detach().numpy(),axis=0)

    return emb_input_mean
def add_embeddings(tensor):
    if tensor.shape[0] == 1:
        #to account for the fact that sometimes they're just one word
        emb_input_add = tensor.detach().numpy()
    else:        
        emb_input_add = np.sum(tensor.detach().numpy(),axis=0)
    
    return np.squeeze(emb_input_add) #squeezing if winds up having an extra axis

def compute_cosine_sim(avg_SML_input1, avg_SML_input2, avg_SML_input3, avg_OML_input1, avg_OML_input2, avg_OML_input3):
    ''' using PyTorch built-in function to compute the cosine similarity between tensors'''
    
    blank1_cs = F.cosine_similarity(avg_SML_input1, avg_OML_input1).item()
    blank2_cs = F.cosine_similarity(avg_SML_input2, avg_OML_input2).item()
    blank3_cs = F.cosine_similarity(avg_SML_input3, avg_OML_input3).item()
    
    avg_blanks = np.mean([blank1_cs, blank2_cs, blank3_cs])
    
    return avg_blanks,blank1_cs,blank2_cs,blank3_cs

def BERT_by_inputs_using_full_context_just_1_parallelized(tokenizer, model, ML1, ML2, ML3, input1, input2, input3):
    sentences = [
        (tokenizer, model, ML1, input1),
        (tokenizer, model, ML1 + input1 + ML2, input2),
        (tokenizer, model, ML1 + input1 + ML2 + input2 + ML3, input3)
    ]
    
    # Run the computations in parallel
    #results = Parallel(n_jobs=-1)(delayed(compute_embeddings)(*args) for args in sentences)
    results = Parallel(n_jobs=-1, backend='threading')(delayed(compute_embeddings)(*args) for args in sentences)
    #print('Getting results in the BERT embeddings, results', results)

    embeddings_input1, embeddings_input2, embeddings_input3 = results

    return embeddings_input1, embeddings_input2, embeddings_input3


def BERT_by_inputs_using_onlyML_context_just_1_parallelized(tokenizer, model, ML1, ML2, ML3, input1, input2, input3):
    
    sentences = [
        (tokenizer, model, ML1, input1),
        (tokenizer, model, ML2, input2),
        (tokenizer, model, ML3, input3)
    ]
    
    # Run the computations in parallel
    results = Parallel(n_jobs=-1, backend='threading')(delayed(compute_embeddings)(*args) for args in sentences)

    embeddings_input1, embeddings_input2, embeddings_input3 = results
    
    
    return embeddings_input1, embeddings_input2, embeddings_input3

def compute_embeddings(tokenizer, model, base_sentence, input_word):
    return extract_word_embeddings_from_sentence_and_add(tokenizer, model, base_sentence, input_word)

def extract_word_embeddings_from_sentence_and_add(tokenizer, model, context, input_text):
    # Combine context and input_text
    full_sentence = context + input_text

    # Tokenize
    encoded_inputs = tokenizer(full_sentence, return_tensors='pt', truncation=True, padding=True)
    input_ids = encoded_inputs['input_ids'][0]
    tokens = tokenizer.convert_ids_to_tokens(input_ids)

    # Get model outputs
    with torch.no_grad():
        outputs = model(**encoded_inputs)
    embeddings = outputs[0][0]  # Shape: [sequence_length, embedding_dimension]

    # Determine where input_text starts in full_sentence
    start_idx = len(tokenizer.tokenize(context))

    # Extract embeddings for input_text
    input_tokens = tokenizer.tokenize(input_text)
    input_embeddings = embeddings[start_idx: start_idx + len(input_tokens)]

    # If length of input_text tokens is more than 1, sum the embeddings
    if len(input_tokens) > 1:
        summed_embedding = torch.sum(input_embeddings, dim=0, keepdim=True)
        return summed_embedding
    else:
        return input_embeddings
    
def get_embed_per_blank_from_sentence(idx1,idx2,idx_end_input,tokens,embeddings,input_here):
    if (idx2 == idx1+1) and idx_end_input > idx2:
        if len(tokens[0]) == embeddings[0].shape[1]:
            #confirming that the sizes are correct! 
            input_ = embeddings[0][0][idx2:idx_end_input+1]
        else:
            print('ERROR!')
    
    else:
        print('ERROR with determining the index of the blank!')
        
        print('Is the problem that the first blank is a repeated word? See if the word before the second index is equal to the previous index')
        if (tokens[0][idx2-1] == tokens[0][idx1]) and idx_end_input > idx2:
            idx1 = idx2-1
            input_ = embeddings[0][0][idx2:idx_end_input+1]
            print(f"Yes looks like that was it! {tokens[0][idx2-1]} was the word with the problem")
        else:
            print('Nope! It looks like the last word in the blank is the repeated word')
                 
        
    if len(input_) == 0:
        print('ERROR')
    return input_


def confirm_idx(comp1,comp2,diff):
    '''comp1 is the one you want the reference from'''
    print('comp1',comp1)
    print('comp2',comp2)
    a=0
    for val in comp1:
        for val2 in comp2:
            if val2+diff == val:
                a = comp1.index(val)
                break
            else:
                None
        
    return comp1[a]      



def commonWords(sent1, sent2):
    
    ''' Gets out the words that are shared between sentences'''
    
    # Splitting the words in a set
    sen1 = set(sent1)
    sen2 = set(sent2)
      
    # Stores the list of common words
    common = list(sen1.intersection(sen2))
      
    # Return the list
    return common
  
# Function to remove all the words
# that are common in both the strings
def removeCommonWords(sent1, sent2):
    
    # Stores the words of the
    # sentences in separate lists
    sentence1 = list(sent1.split())
    sentence2 = list(sent2.split())

    commonlist = commonWords(sentence1, 
                             sentence2)
  
    word = 0
      
    # Iterate the list of words
    # of the first sentence
    for i in range(len(sentence1)):
        
        # If word is common in both lists
        if sentence1[word] in commonlist:
            
              # Remove the word
            sentence1.pop(word)
              
            # Decrease the removed word
            word = word - 1
        word += 1
  
    word = 0
      
    # Iterate the list of words
    # of the second sentence
    for i in range(len(sentence2)):
        
        # If word is common in both lists
        if sentence2[word] in commonlist:
            
              # Remove the word
            sentence2.pop(word)
              
            # Decrease the removed word
            word = word-1
        word += 1
          
      
    sentence1 = " ".join(str(x) for x in sentence1)
    
    exclude = set(string.punctuation)
    sentence1 = ''.join(ch for ch in sentence1 if ch not in exclude)
    return(sentence1,sentence2)
  
