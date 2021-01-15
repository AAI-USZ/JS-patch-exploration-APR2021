# Data for patch correctness study presented at APR 2021 @ICSE

This repository contains open science data used in the paper **Exploring Plausible Patches Using Source Code Embeddings in JavaScript**.

Candidate patches can be found under the `candidate_patches` folder. The `eslint_i` subfolder contains the candidate patches for the `i`-th bug. In these subfolders 3 different naming conventions are used:
 - `Eslint_i_buggy.js`: the original (buggy) program of Eslint_i
 - `Eslint_i_dev.js`: the developer fix
 - `Eslint_i_p.js`: the p-th generated patch candidate
 
 The annotated data for each bug is stored in the `categorizations.json` file. The structure of the json is the following:
 >`{
 "Eslint": {
   "i": {
      "0": s1,
      "1": s2,
      .
      .
      .
      "n": s3
    }
  }
  .
  .
  .
}`

Where:
 - `i` is the identifier of the bug
 - the number of generated patches is `n`
 - `s1, s2, s3` are the relevance scores given for the actual candidate