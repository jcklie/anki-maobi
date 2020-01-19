var writer = HanziWriter.create(config.targetDiv, data.character, {
    width: config.size,
    height: config.size,
    showCharacter: false,
    showOutline: false,
    highlightOnComplete: true,
    leniency: config.leniency,
    padding: 0,
    charDataLoader: function (char, onComplete) {
        var charData = data.characterData;
        onComplete(charData);
    }
});

writer.quiz();