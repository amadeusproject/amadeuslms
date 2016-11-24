
  //Insert question choice
  function showDiv (elem, questionType_id) {
    if (elem.value == 0) {
      var questionChoice =
      '<div id="questionChoice_'+questionType_id+'">' +
          '<div class="row form-group">'+
            '<label for="question-name" class="col-md-2 control-label">Question</label>'+
            '<div class="col-md-10">'+
              '<textarea class="form-control" rows="1" id="question-name" placeholder="Wording"></textarea>'+
            '</div>'+
          '</div>'+
          '<div class="row form-group">'+
            '<label for="alternatives" class="col-md-2 control-label">Alternatives</label>'+
            '<div class="col-md-10" id="radios_'+questionType_id+'">'+
              '<div class="radio radio-primary form-group">'+
                '<label>'+
                  '<input checked type="radio" name="multiple-choice" id="alternative1" value="1">'+
                  '<textarea class="form-control" rows="1" placeholder="Write your alternative"></textarea>'+
                '</label>'+
              '</div>'+
              '<div class="radio radio-primary form-group">'+
                '<label>'+
                  '<input type="radio" name="multiple-choice" id="alternative2" value="2">'+
                  '<textarea class="form-control" rows="1" placeholder="Write your alternative"></textarea>'+
                '</label>'+
              '</div>'+
            '</div>'+
          '</div>'+
          '<div class="row form-group">'+
            '<div class="col-md-8 col-md-offset-2">'+
              '<button type="button" class="btn btn-raised btn-primary" id="newAlternative_'+questionType_id+'" onclick="functionNewAlternative(radios_'+questionType_id+')">New Alternative</button>'+
            '</div>'+
          '</div>'+
        '</div>';
    } else if (elem.value == 1) {
      var questionChoice =
        '<div id="questionChoice_'+questionType_id+'">'+
              '<div class="row form-group">'+
                '<label for="question-name" class="col-md-2 control-label">Question True or False</label>'+
                '<div class="col-md-10">'+
                  '<textarea class="form-control" rows="1" id="question-name" placeholder="Wording"></textarea>'+
                '</div>'+
              '</div>'+
              '<div class="row form-group">'+
                '<label for="alternative" class="col-md-2 control-label">Alternatives: T/F</label>'+
                '<div class="col-md-10" id="radiosTF_'+questionType_id+'">'+
                  '<div class="radio radio-primary form-group" value="1">'+
                      '<label class="primary-label-TF">'+
                        '<textarea class="form-control" rows="1" placeholder="Write your alternative"></textarea>'+
                      '</label>'+
                      '<label>'+
                        '<input type="radio" name="true-or-false-1" value="T">'+
                      '</label>'+
                      '<label>'+
                        '<input type="radio" name="true-or-false-1" value="F">'+
                      '</label>'+
                  '</div>'+
                  '<div class="radio radio-primary form-group" value="2">'+
                      '<label class="primary-label-TF">'+
                        '<textarea class="form-control" rows="1" placeholder="Write your alternative"></textarea>'+
                      '</label>'+
                      '<label>'+
                        '<input type="radio" name="true-or-false-2" value="T">'+
                      '</label>'+
                      '<label>'+
                       '<input type="radio" name="true-or-false-2" value="F">'+
                      '</label>'+
                  '</div>'+
                '</div>'+
              '</div>'+
              '<div class="row form-group">'+
                '<div class="col-md-8 col-md-offset-2">'+
                  '<button type="button" class="btn btn-raised btn-primary" id="newAlternative_'+questionType_id+'" onclick="functionNewAlternativeTF(radiosTF_'+questionType_id+')">New Alternative</button>'+
                '</div>'+
              '</div>'+
            '</div>';
    } else if (elem.value == 3) {
      var questionChoice =
      '<div id="questionChoice_'+questionType_id+'">'+
        '<div class="row form-group">'+
          '<label for="question-name" class="col-md-2 control-label">Name Question discursive</label>'+
          '<div class="col-md-10">'+
            '<textarea class="form-control" rows="2" id="question" placeholder="Wording"></textarea>'+
          '</div>'+
        '</div>'+
      '</div>';
    }
    if(document.getElementById('questionChoice_'+ questionType_id)){
      $('#questionChoice_'+ questionType_id).detach();
    }
    $(questionChoice).insertBefore('#hr_'+questionType_id);
    $('.primary-label-TF').css('padding-left', '0px');
    $.material.init() //O material deve ser iniciado aqui para funcionar os botoes de radio.
  }
//Bug quando criamos sem ser na ordem
function functionNewAlternative(Question_Id){
  var alternative = parseInt($("div input").last().val()) + 1;
   var element = '<div class="radio radio-primary form-group">' +
    '<label>' +
      '<input type="radio" name="alternatives" id="alternative_'+alternative+'_'+Question_Id+'"' + 'value="'+alternative+'">' +
        '<textarea class="form-control" rows="1" placeholder="Write your alternative"></textarea>' +
      '</label>'+
    '</div>';
    $(Question_Id).append(element);
    $.material.init() //O material deve ser iniciado aqui para funcionar os botoes de radio.
}
function functionNewAlternativeTF(Question_Id){
  var alternative = parseInt($("div").last().val()) + 1;
   var element =
    '<div class="radio form-group">'+
      '<label class="primary-label-TF" >'+
        '<textarea class="form-control" rows="1" placeholder="Write your alternative"></textarea>'+
      '</label>'+
      '<label>'+
        '<input type="radio" name="true-or-false-2" value="T">'+
      '</label>'+
      '<label>'+
        '<input type="radio" name="true-or-false-2" value="F">'+
      '</label>'+
    '</div>';
    $(Question_Id).append(element);
    $('.primary-label-TF').css('padding-left', '0px');
    $.material.init() //O material deve ser iniciado aqui para funcionar os botoes de radio.
}