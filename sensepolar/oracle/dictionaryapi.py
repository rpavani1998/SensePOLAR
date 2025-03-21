import requests
from nltk.corpus import wordnet


class Dictionary:
    """
    A class used to access various online dictionaries and get synonyms, antonyms,
    definitions, and examples of a given word.

    Args:
    dictionary_id (str): the id of the dictionary to use (one of 'dictionaryapi',
                         'oxford', 'wordnik', or 'wordnet')
    api_key (str, optional): the api key to use for the chosen dictionary
    source_lang (str, optional): the source language to use for the chosen dictionary

    Attributes:
    dictionary_id (str): the id of the dictionary being used
    api_key (str): the api key being used for the chosen dictionary (None if not required)
    source_lang (str): the source language being used for the chosen dictionary
    urls (dict): a dictionary mapping url types to urls for the chosen dictionary

    Methods:
    _get_urls(): get the urls for the chosen dictionary
    _make_request(url): make a request to the chosen dictionary
    get_synonyms(word): get the synonyms for a given word from the chosen dictionary
    get_antonyms(word): get the antonyms for a given word from the chosen dictionary
    get_definitions(word): get the definitions for a given word from the chosen dictionary
    get_examples(word): get the examples for a given word from the chosen dictionary
    """
    def __init__(self, dictionary_id, api_key=None, source_lang='en_US'):
        """
        Initialize the Dictionary object with the given dictionary_id, api_key (if required),
        and source_lang (if applicable).
        """
        self.dictionary_id = dictionary_id
        self.api_key = api_key
        self.source_lang = source_lang
        self.urls = self._get_urls()

    def _get_urls(self):
        """
        Get the urls for the chosen dictionary based on its dictionary_id.
        """
        urls = {}
        if self.dictionary_id == 'dictionaryapi':
            urls['definitions'] = 'https://api.dictionaryapi.dev/api/v2/entries/{source_lang}/{word}'
            urls['examples'] = 'https://api.dictionaryapi.dev/api/v2/entries/{source_lang}/{word}'
        elif self.dictionary_id == 'oxford':
            urls['definitions'] = 'https://od-api.oxforddictionaries.com/api/v2/entries/{source_lang}/{word_id}'
            urls['examples'] = 'https://od-api.oxforddictionaries.com/api/v2/entries/{source_lang}/{word_id}/sentences'
        elif self.dictionary_id == 'wordnik':
            urls['definitions'] = 'https://api.wordnik.com/v4/word.json/{word}/definitions?limit=100&includeRelated=false&useCanonical=false&includeTags=false&api_key={api_key}'
            urls['examples'] = 'https://api.wordnik.com/v4/word.json/{word}/definitions?limit=100&includeRelated=false&useCanonical=false&includeTags=false&api_key={api_key}'
        elif self.dictionary_id == 'wordnet':
            urls['definitions'] = None
            urls['examples'] = None
        else:
            raise ValueError(f"Dictionary '{self.dictionary_id}' not supported")
        return urls

    def _make_request(self, url):
        """
        Make a request to the chosen dictionary with the given url.
        """
        if self.dictionary_id == 'wordnet':
            params = {'s': url}
            response = requests.get(self.urls['synonyms'], params=params)
            if response.status_code == 200:
                return response.text
            else:
                return None
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return None


    def get_examples(self, word):
        """
        Get the definitions for a given word from the chosen dictionary.
        """
        all_examples = []
        if self.dictionary_id == 'wordnet':
            for synset in wordnet.synsets(word):
                # if len(synset.examples()) == 0:
                #     continue
                all_examples.append(synset.examples())
            # print(len(all_examples),'all_examples', all_examples)
            return all_examples
        url = self.urls['examples'].format(word=word, api_key=self.api_key, source_lang=self.source_lang)
        response = self._make_request(url)
        if response is None:
            return []
        if self.dictionary_id == 'oxford':
            if response and 'results' in response:
                results = response['results']
                for result in results:
                    if 'lexicalEntries' in result:
                        entries = result['lexicalEntries']
                        for entry in entries:
                            if 'sentences' in entry:
                                sentences = entry['sentences']
                                for sentence in sentences:
                                    if 'text' in sentence:
                                        all_examples.append(sentence['text'])

        elif self.dictionary_id == 'dictionaryapi':
            if not isinstance(response, list):
                response = [response]
            for entry in response:
                meanings = entry.get("meanings", [])
                for meaning in meanings:
                    definitions = meaning.get("definitions", [])
                    if definitions:
                        for definition in definitions:
                            example_uses = definition.get("example")
                            if example_uses:
                            #     example_uses = []
                                all_examples.append(example_uses)  
        elif self.dictionary_id == 'wordnik':
            for entry in response:
                if 'text' in entry.keys():
                    definition = entry['text']
                    examples = [example['text'] for example in entry['exampleUses'] if 'text' in example.keys()]
                    # if examples:
                    # #     examples = []
                    all_examples.append(examples)
        else:
            raise ValueError(f"Dictionary '{self.dictionary_id}' not supported")
        return all_examples
        


    def get_definitions(self, word):
        """
        Get the examples for a given word from the chosen dictionary.
        """
        all_definitions = []
        if self.dictionary_id == 'wordnet':
            definitions = []
            for synset in wordnet.synsets(word):
                if len(synset.examples()) == 0:
                    continue
                all_definitions.append([synset.definition()])
            return all_definitions
        url = self.urls['definitions'].format(word=word, api_key=self.api_key, source_lang=self.source_lang)
        response = self._make_request(url)
        if response is None:
            return []
        if self.dictionary_id == 'dictionaryapi':
            if not isinstance(response, list):
                response = [response]
            for entry in response:
                meanings = entry.get("meanings", [])
                for meaning in meanings:
                    definitions = meaning.get("definitions", [])
                    if definitions:
                        for definition in definitions:
                            example_uses = definition.get("example")
                            if example_uses:
                                all_definitions.append([definition.get("definition")])
        elif self.dictionary_id == 'oxford':
            entries = response.get('results', [{}])[0].get('lexicalEntries', [])
            senses = []
            for entry in entries:
                senses += entry.get('entries', [{}])[0].get('senses', [])
            definitions = []
            for sense in senses:
                definitions += sense.get('definitions', [])
        elif self.dictionary_id == 'wordnik':
            for entry in response:
                if 'text' in entry.keys():
                    definition = entry['text']
                    examples = [example['text'] for example in entry.get('exampleUses', []) if example['text']]
                    # if examples:
                    all_definitions.append([definition])
        return list(all_definitions)
    
    def get_synonyms(self, word):
        """
        Get the synonyms for a given word from the chosen dictionary.
        """
        if self.dictionary_id == 'wordnet':
            synonyms = []
            for synset in wordnet.synsets(word):
                for lemma in synset.lemmas():
                    synonym = lemma.name().replace('_', ' ')
                    if synonym != word:
                        synonyms.append(synonym)
            return synonyms
        url = self.urls['synonyms'].format(word=word, api_key=self.api_key, source_lang=self.source_lang)
        response = self._make_request(url)
        if response:
                if self.dictionary_id == 'dictionaryapi':
                    synonyms = response[0].get('meta', {}).get('syns', [])[0]
                elif self.dictionary_id == 'oxford':
                    synonyms = response.get('results', [])[0].get('lexicalEntries', [])[0].get('entries', [])[0].get('senses', [])[0].get('synonyms', [])
                    synonyms = [synonym.get('text') for synonym in synonyms]
                elif self.dictionary_id == 'wordnik':
                    synonyms = response[0].get('words', [])
                return synonyms
        else:
            return None
    
    def get_antonyms(self, word):
        """
        Get the antonyms for a given word from the chosen dictionary.
        """
        if self.dictionary_id == 'wordnet':
                antonyms = []
                for synset in wordnet.synsets(word):
                    for lemma in synset.lemmas():
                        if lemma.antonyms():
                            antonyms.extend([antonym.name() for antonym in lemma.antonyms()])
                if antonyms:
                    return antonyms
        # url = self.urls['antonyms'].format(word=word, api_key=self.api_key, source_lang=self.source_lang)
        response = None
        if response:
            if self.dictionary_id == 'dictionaryapi':
                antonyms = response[0].get('meta', {}).get('ants', [])
                if antonyms:
                    return antonyms[0]
            elif self.dictionary_id == 'oxford':
                antonyms = []
                results = response.get('results', [])
                if results:
                    lexical_entries = results[0].get('lexicalEntries', [])
                    for entry in lexical_entries:
                        entries = entry.get('entries', [])
                        for entry in entries:
                            senses = entry.get('senses', [])
                            for sense in senses:
                                antonym_entries = sense.get('antonyms', [])
                                for antonym_entry in antonym_entries:
                                    antonyms.append(antonym_entry.get('text'))
                if antonyms:
                    return antonyms
            elif self.dictionary_id == 'wordnik':
                antonyms = []
                for result in response:
                    if result.get('relationshipType') == 'antonym':
                        words = result.get('words', [])
                        antonyms.extend(words)
                if antonyms:
                    return antonyms
        return None
    
