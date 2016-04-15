(function () {
    angular.module('drive')
        .controller('UploadController', ['$scope', '$rootScope', 'Upload', '$timeout', function ($scope, $rootScope, Upload, $timeout) {
            $scope.uploadFiles = function (files, errFiles, type) {
                console.log(type);
                $scope.files = files;
                $scope.errFiles = errFiles;
                angular.forEach(files, function (file) {
                    file.upload = Upload.upload({
                        url: '/upload/',
                        data: {file: file, type: type}
                    });

                    file.upload.then(function (response) {
                        $timeout(function () {
                            file.result = response.data;
                        });
                    }, function (response) {
                        if (response.status > 0)
                            $scope.errorMsg = response.status + ': ' + response.data;
                    }, function (evt) {
                        file.progress = Math.min(100, parseInt(100.0 *
                            evt.loaded / evt.total));
                    });
                });
                $rootScope.$emit("FilesUpdated", {});
            }
        }])
        .controller('DashboardController', ['$scope', '$rootScope', '$http', function ($scope, $rootScope,  $http) {
            $scope.userFiles = [];
            $scope.selected = {'E': -1, 'I': -1};
            $scope.relation = {};
            $scope.schedules = [];
            $scope.update_files = function () {
                $http.get('/my_files/').success(function (data) {
                    $scope.userFiles = data;
                    console.log($scope.userFiles);
                    for (key in $scope.userFiles) {
                        $scope.relation[$scope.userFiles[key].id] = key
                    }
                });
            };
            $scope.switch_selection = function (file) {
                if (file.type == 'E' && file.selected==false) {
                    if ($scope.selected['E'] != -1) {
                        $scope.userFiles[$scope.relation[$scope.selected['E']]].selected = false;
                    }
                    $scope.selected['E'] = file.id;
                    file.selected = true;

                } else if(file.selected==false) {
                    if ($scope.selected['I'] != -1) {
                        $scope.userFiles[$scope.relation[$scope.selected['I']]].selected = false;
                    }
                    $scope.selected['I'] = file.id;
                    file.selected = true;
                } else if(file.type == 'E' && file.selected==true) {
                    $scope.selected['E'] = -1;
                    file.selected = false;
                } else if(file.selected==true) {
                    $scope.selected['I'] = -1;
                    file.selected = false;
                }
                console.log($scope.selected);
            };
            $scope.update_schedules = function() {
                $http.get('/my_schedules/').success(function (data) {
                    $scope.schedules = data;
                    console.log($scope.schedules);
                });
            }
            $scope.schedule_execution = function() {
                console.log($scope.selected);
                data = {"executable": $scope.selected['E'], "input_file": $scope.selected['I'] }
                $http.post('/schedule/', data).success(function (data) {
                    $scope.schedules.push(data);
                    console.log($scope.schedules);
                });
            };
            $rootScope.$on("FilesUpdated", function(){
               $scope.update_files();
            });

            $scope.update_files();
            $scope.update_schedules();
        }])
})();