var curCharacterIdx = -1;
var curQuizDiv = undefined;
var prevCharacterDivs = [];

var CHAR_SPACING = 20;


/**
 * Starts the quiz for the next character and
 */
function quizNextCharacter() {
    if (curQuizDiv !== undefined) {
        prevCharacterDivs.unshift(curQuizDiv);
    }
    if (curCharacterIdx < data.characters.length - 1) {
        curCharacterIdx++;
        curQuizDiv = document.createElement("div");
        document.getElementById(config.targetDiv).append(curQuizDiv);
        curQuizDiv.style['margin-left'] = -Math.floor(config.size / 2) + 'px';
        quizCharacter(data.characters[curCharacterIdx], data.charactersData[curCharacterIdx], curQuizDiv);

        // if this is not the first character, we show a fade-in
        if (curCharacterIdx > 0) {
            curQuizDiv.style['margin-left'] = Math.floor(config.size / 2) + CHAR_SPACING + 'px';
            curQuizDiv.style.opacity = '0';

            // let webkit render the content before repositioning the new (new) character div. Otherwise the fade-in
            // animation is ignored
            setTimeout(function () {
                repositionDivs()
            }, 50);
        }
    }
}

/**
 * Repositions all character divs
 */
function repositionDivs() {
    prevCharacterDivs.map(function (div, idx) {
        if (idx < 5) {
            div.style['margin-left'] = Math.floor(-config.size / 2 - (config.size + CHAR_SPACING) * (idx + 1)) + 'px';
        } else {
            div.style.display = 'none';
        }
    });

    curQuizDiv.style['margin-left'] = -Math.floor(config.size / 2) + 'px';
    curQuizDiv.style.opacity = '1';
}

/**
 * Creates and starts the HanziWriter quiz for a given character
 * @param character the character to quiz for
 * @param characterData stroke data
 * @param targetDiv div that should be used for rendering the quiz
 */
function quizCharacter(character, characterData, targetDiv) {
    var writer = HanziWriter.create(targetDiv, character, {
        width: config.size,
        height: config.size,
        showCharacter: false,
        showOutline: false,
        highlightOnComplete: true,
        leniency: config.leniency,
        padding: 0,
        charDataLoader: function (char, onComplete) {
            onComplete(characterData);
        },
        onComplete: function (data) {
            // wait for HanziWriter animation to complete
            setTimeout(quizNextCharacter, 1000);
        }
    });
    writer.quiz();
}


quizNextCharacter();