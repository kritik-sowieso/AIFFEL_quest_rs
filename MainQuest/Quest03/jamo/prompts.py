SYSTEM = '''Convert Korean into the fixed spatial jamo layout. Output only the requested data, without explanation or code fences.
CONVERT: Align every syllable's initial consonant on row 0. For ㅏㅐㅑㅒㅓㅔㅕㅖㅣ put the vowel one cell right; put any final consonant one cell below the initial. For ㅗㅛㅜㅠㅡ put the vowel below the initial and the final consonant below the vowel. Leave one empty cell between syllables, plus two extra cells for each original word space. Keep tense consonants and compound finals as single jamo characters. Preserve punctuation on row 0. Each jamo and ASCII space occupies one grid cell. Trim only row-end spaces. Use actual line breaks.
ANNOTATE: Return the auxiliary annotation in the format specified in the task. The order is left-to-right syllable order and initial-vowel-final within each syllable.'''

def messages(text, task='CONVERT', condition=None):
    if task == 'ANNOTATE':
        form = 'characters separated by semicolons' if condition == 'B' else 'character@x,y entries separated by semicolons; coordinates are zero-based integer grid cells'
        request = f'[TASK=ANNOTATE] Format: {form}. Input: {text}'
    else:
        request = f'[TASK=CONVERT] {text}'
    return [{'role':'system','content':SYSTEM}, {'role':'user','content':request}]
