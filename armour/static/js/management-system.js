$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", token);
        }
    }
});

function ajaxPostRequest(url, params, type = 'json') {
    return new Promise(function (resolve, reject) {
        //make sure the coord is on street
        $.post(url, params).then(function (resp) {
            return resp;
        }, type).then(function (json) {
            if (json) resolve(json)
            else reject()
        });
    });
}

var myApp = angular.module('myApp', []);
myApp.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
});
myApp.controller("docCtrl", function ($scope, $http) {
    $scope.filter_type = '0';
    $scope.filter_period = '0';
    $scope.filter_sign = '2';
    $scope.parent = 0;
    $scope.folders = [];
    $scope.files = [];
    $scope.folder = {};
    $scope.file = {};
    $scope.list = {};
    $scope.focusEle = {};
    angular.element(document).ready(function () {
        $scope.getData();
    });

    $scope.getData = function () {
        ajaxPostRequest(baseUrl, {
            action: 'list',
            level: $scope.parent
        }).then((resp => {
            if (resp.status) {
                $scope.$apply(function () {
                    $scope.folders = resp.folder;
                    $scope.files = resp.file;
                })
            }
        }))
    };


    $scope.addFolder = function () {
        $scope.folder = {cls: '', name: '', id: 0};
        $('#folderModal').modal({backdrop: 'static', keyboard: false});
    };

    $scope.add_file = function () {

        $scope.file = {cls: '', name: '', id: 0, msg: ''};
        $('#fileModal').modal({backdrop: 'static', keyboard: false});
    };


    $scope.save_file = function () {
        if ($scope.file.name == '') {
            $scope.file.cls = 'has-error';
            $scope.file.msg = 'Required Field';
            return false;
        }
        if ($('#file_upload').val() == '')
            return false;
        let formData = new FormData($('#frmFile')[0]);
        $.ajax({
            url: fileUploadUrl,
            dataType:'json',
            type: 'post',
            data: formData,
            cache:false,
            contentType: false,
            processData: false,
            success: function (resp) {
                 $('#fileModal').modal('hide');
                if (resp.status) {
                    $scope.getData()
                }
            }
        });
    };
    $scope.saveFolder = function () {
        if ($scope.folder.name == '') {
            $scope.folder.cls = 'has-error';
            $scope.folder.msg = 'Required field';
            return false;
        }
        ajaxPostRequest(baseUrl, {
            action: 'rename_folder',
            level: $scope.parent,
            id: $scope.folder.id,
            value: $scope.folder.name
        }).then((resp => {
            $('#folderModal').modal('hide');
            const id = resp.id;
            console.log("id====" + id);
            let IsUpdate = false;
            if (resp.status) {
                $scope.$apply(function () {
                    $.each($scope.folders, function (i, j) {
                        if (j.id == id) {
                            console.log('this is update');
                            IsUpdate = true;
                            j.name = $scope.folder.name;
                            return false;
                        }
                    });
                    if (!IsUpdate)
                        $scope.folders.push({id: id, name: $scope.folder.name, parent: $scope.parent})
                })
            }
        }))
    };
    $scope.backParent = function () {
        ajaxPostRequest(baseUrl, {
            action: 'parent',
            level: $scope.parent
        }).then((resp => {
            if (resp.status) {
                $scope.$apply(function () {
                    $scope.folders = resp.folder;
                    $scope.files = resp.file;
                    $scope.parent = parseInt(resp.parent);
                })
            }
        }))
    };

    $scope.enterFolder = function (id, index) {
        $scope.parent = parseInt(id);
        $scope.getData();
    };
    $scope.openFolder = function () {
        $scope.parent = $scope.focusEle.id;
        $scope.getData();
    };
    $scope.editFolder = function () {
        $scope.folder = {cls: '', name: $scope.focusEle.name, id: $scope.focusEle.id};
        $('#folderModal').modal({backdrop: 'static', keyboard: false});
    };
    $scope.deleteFolder = function () {
        $scope.focusEle.type = "Folder";
        $scope.focusEle.action = 'delete_folder';
        $('#actionModal').modal({backdrop: 'static', keyboard: false});
    };
    $scope.confirmDelete = function () {
        console.log($scope.focusEle)
        ajaxPostRequest(baseUrl, {
            action: $scope.focusEle.action,
            level: $scope.focusEle.id
        }).then((resp => {
            $('#actionModal').modal('hide');
            if (resp.status) {
                $scope.$apply(function () {
                    if ($scope.focusEle.action === 'delete_folder') {
                        $.each($scope.folders, function (i, j) {
                            if (j.id == $scope.focusEle.id) {
                                $scope.folders.splice(i, 1);
                                return false;
                            }
                        });
                    } else if($scope.focusEle.action === 'delete_file') {
                        $.each($scope.files, function (i, j) {
                            if (j.id == $scope.focusEle.id) {
                                $scope.files.splice(i, 1);
                                return false;
                            }
                        });
                    }
                })
            }
        }))
    }
    $scope.deleteDoc = function () {
        $scope.focusEle.type = "File";
        $scope.focusEle.action = 'delete_file';
        $('#actionModal').modal({backdrop: 'static', keyboard: false});
    };

    $scope.openDoc = function (key) {
        if (key == null)
            key = $scope.focusEle.sharedKey;
        window.location.href = p_openDoc + key;
    };
    $scope.editDoc = function () {
        $scope.folder = {cls: '', name: $scope.focusEle.name, id: $scope.focusEle.id};
        $('#fileNameModal').modal({backdrop: 'static', keyboard: false});
    };

    $scope.renameDoc = function () {
        if ($scope.folder.name == '') {
            $scope.folder.cls = 'has-error';
            $scope.folder.msg = 'Required Field';
            return false;
        }

        ajaxPostRequest(baseUrl, {
            action: 'rename_file',
            level: $scope.folder.id,
            value: $scope.folder.name
        }).then((resp => {
            $('#fileNameModal').modal('hide');
            if (resp.status) {
                $scope.$apply(function () {
                    $.each($scope.files, function (i, j) {
                        if (j.id == $scope.folder.id) {
                            j.name = $scope.folder.name;
                            return false;
                        }
                    });
                })
            }
        }))
    };

    $scope.downDoc = function () {
        console.log($scope.focusEle)
        $.fileDownload(fileOpenUrl + $scope.focusEle.file);
    };



    $scope.ShowContextMenu = function (value, e) {
        $scope.focusEle = value;
        $('#context' + e).hide();
    };
    $scope.ShowContextMenu2 = function (value, e) {
        $scope.focusEle = value;
        $('#context' + e).hide();
    };

    $('.item-list').on('click', 'div.item-wrap>span.fa-bars', function (e) {
        let findex = $(this)[0].dataset.value;
        e.preventDefault();
        e.stopPropagation();
        let pid = $(this)[0].dataset.id;
        if (pid == '1') {
            $('#context2').hide();
            $scope.focusEle = $scope.folders[findex];
        } else {
            $('#context1').hide();
            $scope.focusEle = $scope.files[findex];
        }
        var ul = $('#context' + pid);
        ul.css({
            position: 'fixed',
            display: 'block',
            left: e.clientX + 'px',
            top: e.clientY + 'px',
        });
    });

    $(document).on('change', '#file_upload', function () {
        let filename = $('input[type=file]').val().replace(/C:\\fakepath\\/i, '');
        //filename = filename.split('.')[0];
        $('#file_name').val(filename);
        $scope.file['name'] = filename;
    });
});

$(document).on('click', 'body', function (e) {
    if ($('.context-menu').is(":visible"))
        $('.context-menu').hide();
});