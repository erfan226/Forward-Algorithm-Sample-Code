import json


def read_json(fn):
    """Convert a json corpus to a dictionary

    Args:
        fn (str): Name of the json file to open

    Returns:
        dict: Converted json to dictionary consisting word counts
    """
    with open(fn) as json_file:
        data = json.load(json_file)
    return data


def compute_start_probability(s_word, category):
    """Generate the start probability of the sentence

    Args:
        s_word (str): First word of the sentence
        category (str): Lexical category of the word to check

    Returns:
        int: Starting probabilities
    """
    start_prob = lex_prob(s_word, category) * \
        compute_bigram_prob("empty", category)
    show_results([(s_word, category, start_prob)])
    return start_prob


def lex_prob(word, category):
    """Compute lexical generation probabilities from corpus

    Args:
        word (str): A word from the sentence
        category (str): Lexical category of the word to compute

    Returns:
        int: Lexical generation probability of the given word
    """
    return corpus["category_word_counts"][word][category] / \
        corpus["category_word_counts"]["total"][category]


def compute_bigram_prob(pre_cat, current_cat):
    """Bigram probability from the sentence

    Args:
        pre_cat (str): Lexical category of the preceding word
        current_cat (str): Lexical category of the curren word in the sentence

    Returns:
        int: Bigram probability of two words, occuring together
    """
    if pre_cat not in corpus["word_pair_count"][current_cat]:
        return 0
    return corpus["word_pair_count"][current_cat][pre_cat] / corpus["total_counts"][pre_cat]


def normalize(word_probs, total_prob):
    """Normalize the probability of lexical category of the word in the sentence by dividing computed probabilities over the overall probability

    Args:
        word_probs (list): Probability of each possibile combination of lexical categories occuring after another
        total_prob (int): Overall probability of the sequence at each full iteration

    Returns:
        int: Normalized probability of the word, i.e. the computed lexical category probabilities of the word
    """
    probs_by_category = []
    for i in word_probs:
        probs_by_category.append((i[0], i[1], i[2] / total_prob))
    return probs_by_category


def show_results(res):
    for i in res:
        print(f"{i[0]} ({i[1]}): {round(i[2], 3)}")


def est_forward(sentence, verbose=False):
    """Run forward algorithm. Thorough two iterations, it'll first go over each word then the word preceding it and then computes their probabilities.
    Then it'll 

    Args:
        sentence ([type]): [description]
        verbose (bool, optional): [description]. Defaults to False.
    """
    sequence_prob = 0
    for word in sentence[1:]:
        word_probs = []
        lex_seq_probs = []
        for i in corpus["category_word_counts"][word]:
            seq_sum = 0
            for j in corpus["category_word_counts"][sentence[sentence.index(word)-1]]:
                # Compute probability of the sentence to begin with a lexical category. Will run only for the first word
                s_prob = compute_start_probability(sentence[0], j) if sentence.index(
                    word) <= 1 else sequence_prob
                lexical_gen_prob = lex_prob(
                    sentence[sentence.index(word)], i)
                bigram_prob = compute_bigram_prob(j, i)
                seq_prob = bigram_prob * s_prob * lexical_gen_prob
                if verbose:
                    print("\n"
                          f"P({word}|{i} {sentence[sentence.index(word)-1]}|{j})=P({i}|{j})*P({' '.join(sentence[:sentence.index(word)])})*P({word}|{i})")
                    print(
                        f"{round(bigram_prob, 5)}*{round(seq_sum, 5)}*{round(lexical_gen_prob, 5)} = {sequence_prob}")
                seq_sum += seq_prob
            word_probs.append((word, i, seq_sum))
            lex_seq_probs.append(seq_sum)
        sequence_prob = sum(lex_seq_probs)
        res = normalize(word_probs, sequence_prob)
        show_results(res)


# We can calculate lexical probabilities for other words as well, if we expand our corpus enough to cover those words.
# Words that are not in the corpus would cause the program to crash!
s1 = "the flies like flower".split()
s2 = "the flies flower like".split()

# This will be used mostly for lexical generation probabilities
corpus = read_json("corpus.json")

# Check to True to see all the hidden calculations
est_forward(s1, False)
