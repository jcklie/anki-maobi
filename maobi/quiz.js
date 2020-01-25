var curCharacterIdx = -1;
var curQuizDiv = undefined;
var curWriter = undefined;
var prevCharacterDivs = [];

var CHAR_SPACING = 20;

var revealAnimationInProgress = false;
var revealButton = document.getElementById(config.revealButton);
var targetDiv = document.getElementById(config.targetDiv);

var TONE_COLORS = getToneColors();

/**
 * Starts the quiz for the next character and moves all previous characters to the left
 */
function quizNextCharacter() {
    if (curQuizDiv !== undefined) {
        prevCharacterDivs.unshift(curQuizDiv);
    }
    if (curCharacterIdx < data.characters.length - 1) {
        curCharacterIdx++;
        curQuizDiv = document.createElement("div");
        targetDiv.append(curQuizDiv);
        curQuizDiv.style['margin-left'] = -Math.floor(config.size / 2) + 'px';

        var character = data.characters[curCharacterIdx];
        var characterData = data.charactersData[curCharacterIdx];
        var toneColor = data.tones.length > 0 ? TONE_COLORS[data.tones[curCharacterIdx]] : '#555555';
        quizCharacter(character, characterData, toneColor, curQuizDiv);

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
    } else {
        try {
            if (revealButton) revealButton.disabled = true;
        } catch (e) {
            console.error(e);
        }
    }
}

/**
 * Repositions all character divs (thereby triggering css animations)
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
 * @param toneColor color of the tone
 * @param targetDiv div that should be used for rendering the quiz
 */
function quizCharacter(character, characterData, toneColor, targetDiv) {
    curWriter = HanziWriter.create(targetDiv, character, {
        width: config.size,
        height: config.size,
        showCharacter: false,
        showOutline: false,
        highlightOnComplete: true,
        leniency: config.leniency,
        padding: 0,
        delayBetweenStrokes: 200,
        strokeColor: toneColor,
        showHintAfterMisses: config.showHintAfterMisses || Number.MAX_SAFE_INTEGER, // setting showHintAfterMisses to
        // false does not disable the feature
        charDataLoader: function (char, onComplete) {
            onComplete(characterData);
        },
        onComplete: function (data) {
            // wait for HanziWriter finish animation
            curWriter = undefined;
            setTimeout(quizNextCharacter, 200);
        }
    });
    curWriter.quiz();
}

/**
 * Stops the quiz, reveals the current character, and animates it. Then starts the quiz for this character again
 */
function revealCurrentCharacter() {
    if (!revealAnimationInProgress) {
        revealAnimationInProgress = true;
        curWriter.cancelQuiz();
        curWriter.showOutline();
        curWriter.animateCharacter({
            onComplete: function () {
                setTimeout(function () {
                    curWriter.hideCharacter();
                    curWriter.quiz();
                    revealAnimationInProgress = false;
                }, 1000);
            }
        });
        curWriter.showOutline = true;
    }
}

/**
* @return the computed color values of the tone colors
*/
function getToneColors() {
    var colors = {};
    for (var i = 1; i <= 5; i++) {
        var toneName = 'tone' + i;
        var tmpSpan = document.createElement('span');
        tmpSpan.className = toneName;
        document.body.appendChild(tmpSpan);
        var color = getComputedStyle(tmpSpan).color;
        document.body.removeChild(tmpSpan);
        colors[toneName] = color;
    }
    return colors;
}


// Init
// If there is no quiz div, we cannot start maobi
if(targetDiv){
    quizNextCharacter();
} else {
    console.log('Maobi: target div not found: #' + config.targetDiv);
}

if (revealButton) {
    var revealButtonInnerBtn = document.createElement("button");
    revealButtonInnerBtn.textContent = revealButton.getAttribute("label") || 'Reveal';
    revealButton.append(revealButtonInnerBtn);

    revealButtonInnerBtn.addEventListener('click', function () {
        revealCurrentCharacter();
    });
}