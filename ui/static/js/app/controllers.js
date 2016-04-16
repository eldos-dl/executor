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
            $scope.selectedFilesToSchedule = {'E': -1, 'I': -1};
            $scope.selectedFiles = [];
            $scope.selected = 0;
            $scope.relation = {};
            $scope.schedules = [];
            $scope.update_files = function () {
                $http.get('/my_files/').success(function (data) {
                    $scope.userFiles = data;
                    console.log($scope.userFiles);
                    for (key in $scope.userFiles) {
                        $scope.relation[$scope.userFiles[key].id] = key;
                    }
                });
            };
            $scope.switch_selection = function (file) {
                if (file.type == 'E' && file.selected==false) {
                    //if ($scope.selectedFilesToSchedule['E'] != -1) {
                    //    $scope.userFiles[$scope.relation[$scope.selectedFilesToSchedule['E']]].selected = false;
                    //}
                    $scope.selectedFilesToSchedule['E'] = file.id;
                    $scope.selectedFiles.push(file.id);
                    $scope.selected += 1;
                    file.selected = true;

                } else if(file.selected==false) {
                    //if ($scope.selectedFilesToSchedule['I'] != -1) {
                    //    $scope.userFiles[$scope.relation[$scope.selectedFilesToSchedule['I']]].selected = false;
                    //}
                    $scope.selectedFilesToSchedule['I'] = file.id;
                    $scope.selectedFiles.push(file.id);
                    $scope.selected += 1;
                    file.selected = true;

                } else if(file.type == 'E' && file.selected==true) {
                    $scope.selectedFilesToSchedule['E'] = -1;
                    $scope.selectedFiles.splice($scope.selectedFiles.indexOf(file.id), 1);
                    $scope.selected -= 1;
                    file.selected = false;

                } else if(file.selected==true) {
                    $scope.selectedFilesToSchedule['I'] = -1;
                    $scope.selectedFiles.splice($scope.selectedFiles.indexOf(file.id), 1);
                    $scope.selected -= 1;
                    file.selected = false;
                }
                console.log($scope.selectedFilesToSchedule);
            };
            $scope.switch_all_files = function() {
                if ($scope.selected == 0) {
                    for (key in $scope.userFiles) {
                        $scope.userFiles[key].selected = true;
                        $scope.selectedFiles.push($scope.userFiles[key].id);
                    }
                    $scope.selected = $scope.userFiles.length;
                } else {
                    for (key in $scope.userFiles) {
                        $scope.userFiles[key].selected = false;
                    }
                    $scope.selected = 0;
                }
                $scope.selectedFiles.splice(0, $scope.selectedFiles.length);
                $scope.selectedFilesToSchedule = {'E': -1, 'I': -1};
                console.log($scope.userFiles.length);
                console.log($scope.selected);
            };
            $scope.update_schedules = function() {
                $http.get('/my_schedules/').success(function (data) {
                    $scope.schedules = data;
                    console.log($scope.schedules);
                });
            };
            $scope.schedule_execution = function() {
                console.log($scope.selectedFilesToSchedule);
                data = {"executable": $scope.selectedFilesToSchedule['E'], "input_file": $scope.selectedFilesToSchedule['I'] }
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