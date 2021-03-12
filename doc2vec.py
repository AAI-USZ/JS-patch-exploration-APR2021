from typing import Dict
import os
import json
import pickle
from multiprocessing import cpu_count
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import tokenizer


# ALL_1: 256, 32, 2, 40
# ALL_2: 256, 16, 2, 30
# ESLINT_1: 256, 5, 2, 50
VECTOR_SIZE = 256
WINDOW_SIZE = 5
MIN_COUNT = 2
EPOCHS = 50
WORKERS = cpu_count()
ORIGINALS_PATH = '../genprogJS/originals'
DEV_FIX_PATH = '../genprogJS/dev_fixes'
CANDIDATES_PATH = '../genprogJS/candidates/generator/2020-10-14'
PROJECT_FILTER = ['Eslint']
BASE_FILE_NAMES = [
    os.path.splitext(file_name)[0]
    for file_name in os.listdir(ORIGINALS_PATH)
    if file_name.endswith('.js') and any(file_name.startswith(project) for project in PROJECT_FILTER)
]
FILE_COLLECTION = [
    root + os.path.sep + file_name
    for root, directories, file_names in os.walk(CANDIDATES_PATH)
    for file_name in file_names
]
POSITIONS: Dict[str, int] = json.load(open(ORIGINALS_PATH + os.path.sep + 'pos.json'))


def read_originals() -> Dict[str, str]:
    return {
        base: open(ORIGINALS_PATH + os.path.sep + base + '.js', 'r', encoding='utf-8').read()
        for base in BASE_FILE_NAMES
    }


def read_dev_fixes() -> Dict[str, str]:
    return {
        base: open(DEV_FIX_PATH + os.path.sep + base + '.js', 'r', encoding='utf-8').read()
        for base in BASE_FILE_NAMES
    }


def read_patches() -> Dict[str, tuple]:
    return {
        base: tuple(
            (
                (fn:=os.path.splitext(os.path.basename(file_name))[0])[fn.rfind('_') + 1:],
                open(file_name, 'r', encoding='utf-8').read()
            ) for file_name in filter(
                lambda name: os.path.basename(name).startswith(base + '_') and name.endswith('.js'),
                FILE_COLLECTION
            )
        )
        for base in BASE_FILE_NAMES
    }


def cut_patch_as_origin(base: str, origin: str, patch: str):
    line_num = origin.count('\n')
    return '\n'.join(line.strip() for line in patch.splitlines()[POSITIONS[base]:POSITIONS[base] + line_num])


original_contents = read_originals()
dev_fix_contents = read_dev_fixes()
patch_contents = read_patches()
patch_contents = {
    key: tuple(
        (index_tag, cut_patch_as_origin(key, original_contents[key], patch))
        for index_tag, patch in patches
    ) for key, patches in patch_contents.items()
}

tagged_tokenized_patches = [
    ((key, index_tag), tokenizer.js_tokenizer(doc))
    for key, patches in patch_contents.items()
    for index_tag, doc in patches
] + [
    ((key, 'dev_fix'), tokenizer.js_tokenizer(doc))
    for key, doc in dev_fix_contents.items()
]
tokenized_originals = [tokenizer.js_tokenizer(doc) for doc in original_contents.values()]

tagged_docs = [TaggedDocument(doc, [tag]) for tag, doc in tagged_tokenized_patches]

models = [(
    m:=Doc2Vec(
        tagged_docs,
        vector_size=VECTOR_SIZE,
        window=WINDOW_SIZE,
        min_count=MIN_COUNT,
        workers=WORKERS,
        epochs=EPOCHS
    ),
    {
        base: m.docvecs.most_similar(positive=[vector], topn=m.corpus_count)
        for base, vector in zip(BASE_FILE_NAMES, [m.infer_vector(tokens) for tokens in tokenized_originals])
    }
) for _ in range(10)]

pickle.dump(models, open('models.pk', 'wb'), pickle.HIGHEST_PROTOCOL)

exit(0)
