import pandas
import pandas as pd

LETTER_WEIGHT = 1.0
POSITION_WEIGHT = 0.1


def get_corncob(word_length: int) -> list:
    corncob_wordlist = []
    with open('corncob_lowercase.txt', "r", ) as f:
        lines = f.readlines()
    for line in lines:
        if len(line) == word_length+1:
            corncob_wordlist.append(line.strip("\n"))
    return corncob_wordlist


def get_wordle_metrics(reference: list, test_word_list: list) -> (int, int):
    letter_metric = 0
    position_metric = 0
    letter_list = []

    for test_word in test_word_list:
        letter_list.extend(test_word)

        for letter1, letter2 in zip(reference, test_word):
            if letter1 == letter2:
                position_metric += 1

    for letter in set(letter_list):
        if letter in reference:
            letter_metric += 1

    return letter_metric, position_metric


def get_aggregate_wordle_metric(word_list: list, test_word_list: list) -> (list, list):
    total_letter_metric = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    total_position_metric = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    norm_add = 1/len(word_list)
    for word in word_list:
        letter_metric, position_metric = get_wordle_metrics(word, test_word_list)
        total_letter_metric[letter_metric] += norm_add
        total_position_metric[position_metric] += norm_add
    return total_letter_metric, total_position_metric


def get_wordle_score(letter_metric: list, position_metric: list) -> float:
    weights_letter = [x * LETTER_WEIGHT for x in range(0, 6)]
    addition_vector_letter = [a*b for a, b in zip(weights_letter, letter_metric)]

    weights_position = [x * POSITION_WEIGHT for x in range(0, 6)]
    addition_vector_position = [a*b for a, b in zip(weights_position, position_metric)]
    score = sum(addition_vector_letter) + sum(addition_vector_position)
    return score


def get_wordle_score_df(reference_word_list: list, test_word_list: list) -> pd.DataFrame:
    letter_metric_list = []
    position_metric_list = []
    score_list = []
    for word in test_word_list:
        letter_metric, position_metric = get_aggregate_wordle_metric(reference_word_list, [word])
        letter_metric_list.append(letter_metric)
        position_metric_list.append(position_metric)
        score_list.append(get_wordle_score(letter_metric, position_metric))

    wordle_score_df = pd.DataFrame({"word": test_word_list,
                                    "score": score_list,
                                    "letter_metric": letter_metric_list,
                                    "position_metric": position_metric_list})
    return wordle_score_df


def filter_wordlist(initial_wordlist: list, test_word: list):
    filtered_wordlist = []
    for word in initial_wordlist:
        test_array = [letter in word for letter in test_word]
        if not any(test_array):
            filtered_wordlist.append(word)
    return filtered_wordlist


def get_two_word_score_df(wordlist: list, wordle_df: pandas.DataFrame) -> pandas.DataFrame:
    first_word_list = []
    first_word_score_list = []
    first_word_letter_metric_list = []
    first_word_position_metric_list = []

    second_word_list = []
    second_word_score_list = []
    second_word_letter_metric_list = []
    second_word_position_metric_list = []

    total_letter_metric_list = []
    total_position_metric_list = []
    total_score_list = []
    # Only evaluates the highest scored N first words
    for i in range(0, 200):
        first_word = wordle_df.word.iloc[i]
        first_word_score = wordle_df.score.iloc[i]
        first_word_letter_metric = wordle_df.letter_metric.iloc[i]
        first_word_position_metric = wordle_df.position_metric.iloc[i]

        reduced_wordlist = filter_wordlist(wordlist, first_word)
        wordle_df_2 = get_wordle_score_df(wordlist, reduced_wordlist).sort_values(by=["score"], ascending=False)

        second_word = wordle_df_2.word.iloc[0]
        second_word_score = wordle_df_2.score.iloc[0]
        second_word_letter_metric = wordle_df_2.letter_metric.iloc[0]
        second_word_position_metric = wordle_df_2.position_metric.iloc[0]

        first_word_list.append(first_word)
        first_word_score_list.append(first_word_score)
        first_word_letter_metric_list.append(first_word_letter_metric)
        first_word_position_metric_list.append(first_word_position_metric)
        second_word_list.append(second_word)
        second_word_score_list.append(second_word_score)
        second_word_letter_metric_list.append(second_word_letter_metric)
        second_word_position_metric_list.append(second_word_position_metric)

        total_letter_metric, total_position_metric = get_aggregate_wordle_metric(
            wordlist, [first_word, second_word])
        total_score_list.append(get_wordle_score(total_letter_metric, total_position_metric))
        total_letter_metric_list.append(total_letter_metric)
        total_position_metric_list.append(total_position_metric)

    final_df = pd.DataFrame({
        "total_score": total_score_list,
        "total_letter_metric": total_letter_metric_list,
        "total_position_metric": total_position_metric_list,
        "first_word": first_word_list,
        "first_word_score": first_word_score_list,
        "first_word_letter_metric": first_word_letter_metric_list,
        "first_word_position_metric": first_word_position_metric_list,
        "second_word": second_word_list,
        "second_word_score": second_word_score_list,
        "second_word_letter_metric": second_word_letter_metric_list,
        "second_word_position_metric": second_word_position_metric_list
    }).sort_values(by=["total_score"], ascending=False)
    return final_df


def get_letters(wordlist: list) -> list:
    total_str = ""
    for word in wordlist:
        total_str += word
    letters = sorted(list(set(total_str)))
    return letters


def floor_1(number: int) -> int:
    if number > 1:
        number = 1
    return number


def get_letter_stats_df(wordlist: list) -> pandas.DataFrame:
    letters = get_letters(wordlist)
    norm_occurrence_list = []
    norm_word_occurrence_list = []
    for letter in letters:
        fkt = lambda x: stats_fkt(letter, x)
        occurrences = map(fkt, wordlist)
        sum_occurrences = [0, 0, 0, 0, 0, 0]
        word_occurrence = 0
        for occurrence in occurrences:
            sum_occurrences = [a + b for a, b in zip(sum_occurrences, occurrence)]
            word_occurrence += floor_1(sum(occurrence))
        norm_occurrence = [float(x)/len(wordlist) for x in sum_occurrences]
        norm_word_occurrence = float(word_occurrence)/len(wordlist)
        norm_occurrence_list.append(norm_occurrence)
        norm_word_occurrence_list.append(norm_word_occurrence)

    prep_array = []
    for letter, occurrence, word_occurrence in zip(letters, norm_occurrence_list, norm_word_occurrence_list):
        line = [letter]
        line.extend(occurrence)
        line.append(word_occurrence)
        prep_array.append(line)

    column_names = ["letter", "first", "second", "third", "fourth", "fifth", "word_occurrence"]
    return_df = pandas.DataFrame(prep_array, columns=column_names)
    return return_df


def stats_fkt(letter: str, word: str) -> list:
    occurrence = []
    for wor in word:
        if wor == letter:
            occurrence.append(1)
        else:
            occurrence.append(0)
    return occurrence


def main():
    wordlist = get_corncob(5)

    # generates some statistics about letters in wordle words
    letter_df = get_letter_stats_df(wordlist).sort_values(by=["word_occurrence"], ascending=False)
    letter_df.to_csv("letter_analysis.csv")

    # generates statistic about simple two word strategies
    wordle_df = get_wordle_score_df(wordlist, wordlist).sort_values(by=["score"], ascending=False)
    two_word_df = get_two_word_score_df(wordlist, wordle_df)
    two_word_df.to_csv("word_analysis.csv")


if __name__ == '__main__':
    main()
