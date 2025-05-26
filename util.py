
traits = {
    "Openness": [],
    "Conscientiousness": [],
    "Extraversion": [],
    "Agreeableness": [],
    "Neuroticism": []
}


def extract_traits(responses):

    for q_num, response in responses.items():
        q_num = int(q_num)  # Convert string keys to integers

        trait_index = (q_num - 1) % 5

        if trait_index == 0:
            traits["Openness"].append(response)
        elif trait_index == 1:
            traits["Conscientiousness"].append(response)
        elif trait_index == 2:
            traits["Extraversion"].append(response)
        elif trait_index == 3:
            traits["Agreeableness"].append(response)
        elif trait_index == 4:
            traits["Neuroticism"].append(response)

    for trait, values in traits.items():
        print(f"{trait}: {' '.join(map(str, values))}")


def prints():
    print(traits)


def calculate_average_values():
    avg_scores = {}
    scores = []
    # Clear/reset structures (not strictly necessary since we just initialized them)
    avg_scores.clear()
    scores.clear()

    for trait, values in traits.items():
        # Convert strings to floats if they are digits
        numeric_values = [
            float(value) for value in values if value.replace('.', '', 1).isdigit()]
        if numeric_values:  # Avoid division by zero
            avg = sum(numeric_values) / 50
            avg_scores[trait] = avg
            scores.append(avg)
        else:
            avg_scores[trait] = 0
            scores.append(0)

    return scores
