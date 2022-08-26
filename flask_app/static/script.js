$('textarea').keyup(function() {
    
    var characterCount = $(this).val().length,
        current = $('#current')
        current.text(characterCount)
    })