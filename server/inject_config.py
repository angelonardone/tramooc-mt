#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import numpy as np
import json
import yaml


DESC = "Adds special node including s2s options to Nematus model.npz file."
S2S_SPECIAL_NODE = "special:model.yml"


def inject_config(json_path, model_path, force=False):
    print("Loading config {}".format(json_path))
    with open(json_path) as json_io:
        nematus_config = json.load(json_io)

    s2s_config = {
        "type": "nematus",
        "dim-vocabs": [nematus_config["n_words_src"], nematus_config["n_words"]],
        "dim-emb": nematus_config["dim_word"],
        "dim-rnn": nematus_config["dim"],
        "enc-type": "bidirectional",
        "enc-cell": "gru-nematus",
        "enc-cell-depth": nematus_config["enc_recurrence_transition_depth"],
        "enc-depth": nematus_config["enc_depth"],
        "dec-cell": "gru-nematus",
        "dec-cell-base-depth": nematus_config["dec_base_recurrence_transition_depth"],
        "dec-cell-high-depth": nematus_config["dec_high_recurrence_transition_depth"],
        "dec-depth": nematus_config["dec_depth"],
        "layer-normalization": nematus_config["layer_normalisation"],
        "tied-embeddings": nematus_config["tie_decoder_embeddings"],
        "skip": False,
        "special-vocab": [],
    }

    print("Loading model {}".format(model_path))
    model = np.load(model_path)

    if S2S_SPECIAL_NODE in model:
        print("Found the following s2s parameters in model:\n")
        print(model[S2S_SPECIAL_NODE])
        if not force:
            print("Use -f/--force to overwrite")
            return False

    s2s_node = str.encode(yaml.dump(s2s_config).strip()).strip()
    s2s_model = {S2S_SPECIAL_NODE: s2s_node}

    print("Updating model...")
    for tensor_name in model:
        if tensor_name != S2S_SPECIAL_NODE:
            s2s_model[tensor_name] = model[tensor_name]

    np.savez(model_path, **s2s_model)
    return True


def parse_args():
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument(
        "-j", "--json", help="nematus config (model.npz.json)", required=True)
    parser.add_argument(
        "-m", "--model", help="nematus model (model.npz)", required=True)
    parser.add_argument(
        "-f", "--force", help="", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    inject_config(args.json, args.model, args.force)
