function filterTag(tag) {
    all_pokemon = document.getElementsByClassName("pokemon")
    relevant    = document.getElementsByClassName(tag)
    for (p of all_pokemon) {
        p.classList.add("hidden")
    }
    for (p of relevant) {
        p.classList.remove("hidden")
    }
}