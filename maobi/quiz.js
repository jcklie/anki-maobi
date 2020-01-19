var writer = HanziWriter.create(config.targetDiv, data.characters[0], {
    width: config.size,
    height: config.size,
    showCharacter: false,
    showOutline: false,
    highlightOnComplete: true,
    leniency: config.leniency,
    padding: 0,
    charDataLoader: function (char, onComplete) {
        var charData = data.charactersData[0];
        onComplete(charData);
    }
});

writer.quiz();