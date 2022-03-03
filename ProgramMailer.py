from __future__ import annotations

def main():

    # Open the schedule markup file
    with open("../ProgramAnalyzer/Program participant schedules markup.txt", "r") as file:
        markuplines=file.readlines()

    # <person>xxxx</person>
    # <person>xxxx</person>
    # <person>xxxx</person>

    # Each xxxx is:
    # <fullname>fffff</fullname>
    # <email>eeeee</email>
    # <item>iiii</item>
    # <item>iiii</item>
    # <item>iiii</item>
    # <item>iiii</item>

    # Each item is:
    # <title>ttt</title>
    # <participants>pppp</participants>
    # <precis>yyyyy</precis>

    # Markup is a dict keyed by the <name></name> with contents the contained markup and rooted at "main"
    markup: list[dict|list[str]]=resolve(markuplines)



def resolve(markup: list[str]) -> list[dict]:
    # Replace the list of strings with a list of dicts for each xxx and then call resolve for each of those
    # Find the first (perhaps only) markup in the list of strings
    i=0
    return []


if __name__ == "__main__":
    main()