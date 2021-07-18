function show_edit_space(id, category) {
    var index = id.split("_")[1];
    var editable_display = document.getElementById(category+'-display_'+index);
    editable_display.style.display = "None";
    var editable_edit = document.getElementById(category+'-edit_'+index);
    editable_edit.style.display = "block";

    var editable_content = document.getElementById(category+'-e_'+index);
    editable_content.focus();
    var strLength = editable_content.value.length * 2;
    editable_content.setSelectionRange(strLength, strLength);
}

function cancel_edit_space(id, category) {
    var index = id.split("_")[1];
    var editable_display = document.getElementById(category+'-display_'+index);
    editable_display.style.display = "block";
    var editable_edit = document.getElementById(category+'-edit_'+index);
    editable_edit.style.display = "None";

    var editable_content = document.getElementById(category+'-e_'+index);
    editable_content.value = editable_content.getAttribute('ori_value');
}



var app_missed = angular.module('appMissed', []);

app_missed.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
}]);

app_missed.controller('ctrlMissed', function ctrl($scope, $http) {
    $scope.data_missed = [];
    
    $scope.getDataMissed = function getDataMissed() {
        $http.post('/view_missed', {params:{}})
        .success(function(response)
            {
                $scope.data_missed = response.data;
            }
        );
    };

    $scope.submitForm = function submitForm(target, job) {
        var form = document.getElementById('form-'+job+'_'+target.id);
        var form_data = {};
        for (i = 0; i < form.elements.length; i++) {
            var elem = form.elements[i];
            if (elem.type != 'submit') form_data[elem.name] = elem.value;
        }

        $http.post(form_data['url'], form_data)
        .success(function(response)
            {
                $scope.dummy = form_data;
                $scope.getDataMissed();
            }
        );
    };
});