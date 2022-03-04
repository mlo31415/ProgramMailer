from __future__ import annotations

from HelpersPackage import FindAnyBracketedText

def main():

    # Open the schedule markup file
    markuplines=""
    with open("../ProgramAnalyzer/reports/Program participant schedules markup.txt", "r") as file:
        markuplines=file.read()
    # Remove newlines *outside* markup
    markuplines=markuplines.replace(">\n<", "><")

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
    markup: list[tuple[str, str|list]]=resolve([("Main", markuplines)])

    # Now we have the whole schmeer in a hierarchical structure
    # Generate the output
    with open("Program participant schedules email.txt", "w") as file:
        main=markup[0][1]
        for person in main:
            fullname=""
            email=""
            items=""
            for attribute in person[0][1]:
                if attribute[0][0] == "email":
                    email=attribute[0][1]
                if attribute[0][0] == "fullname":
                    fullname=attribute[0][1]
                if attribute[0][0] == "item":
                    title=""
                    participants=""
                    precis=""
                    for subatt in attribute[0][1]:
                        if subatt[0][0] == "title":
                            title=subatt[0][1]
                        if subatt[0][0] == "participants":
                            participants=subatt[0][1]
                        if subatt[0][0] == "precis":
                            precis=subatt[0][1]
                    item=f"{title}\n{participants}\n"
                    if len(precis) > 0:
                        item+=f"{precis}\n"
                    items=items+item+"\n"
            print(f"\n\n\nDear {fullname}\n{email}\n\nHere's yer schedule:\n{items}", file=file)


# Recursively parse the markup
def resolve(markup: list[tuple[str, str]]) -> list[tuple[str, list[tuple[str, str]]]]:
    # Replace the list of strings with a list of dicts for each xxx and then call resolve for each of those
    # Find the first (perhaps only) markup in the list of strings

    assert len(markup) == 1
    key=markup[0][0]
    text=markup[0][1]
    out=[]
    while len(text) > 0:
        lead, bracket, contents, trail=FindAnyBracketedText(text)
        if bracket == "" and contents == "":
            if trail != "":
                # print(f"[({key}, {trail})]")
                return [(key, trail)]
            if trail == "":
                break
        out.append(resolve([(bracket, contents)]))
        text=trail

    # print(f"[({key}, {len(out)=})]")
    return [(key, out)]


if __name__ == "__main__":
    main()