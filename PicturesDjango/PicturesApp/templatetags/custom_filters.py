from django import template

register = template.Library()


#allow to replace _ by / in the html templates
@register.filter(name='replace_underscore')
def replace_underscore(value):
    return value.replace('_', '/')


@register.filter(name='proper_case')
def proper_case(value):
    if not value:
        return value

    # Calculer le pourcentage de majuscules
    lower_count = sum(1 for c in value if c.isalpha() and c.islower())
    upper_count = sum(1 for c in value if c.isalpha() and c.isupper())
    total_alpha = lower_count + upper_count

    if total_alpha == 0:
        return value  # Pas de caractères alphabétiques

    if upper_count / total_alpha <= 0.5:
        return value  # Déjà en proper case ou moins de 50% en majuscules

    def title_case_word(word):
        if "'" in word:
            return word
        return word[0].upper() + word[1:].lower()
    return ' '.join(title_case_word(word) for word in value.split())