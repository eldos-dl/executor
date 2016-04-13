(function(){
    angular.module('drive')
        .controller('UploadController', ['$scope', 'Upload', '$timeout', function($scope, Upload, $timeout) {
            $scope.uploadFiles = function(files, errFiles, type) {
                    console.log(type);
                    $scope.files = files;
                    $scope.errFiles = errFiles;
                    angular.forEach(files, function(file) {
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
                }
        }])
        .controller("LinkController", ['$scope', '$http', function($scope, $http) {
            $scope.url = '';
            $scope.loading = false;
            $scope.saving = false;
            $scope.submit_url = function() {
                console.log($scope.url);
                var requestData = {"url": $scope.url};
                if($scope.url != undefined) {
                    $scope.saving = true;
                    $http.post('/getCacheDetails/', requestData).then(function(data) {
                        $scope.saved = data.data;
                        console.log($scope.saved);
                        $scope.saving = false;
                    }, function(data) {
                        console.log(data);
                        $scope.saving = false;
                    });
                    $scope.loading = true;
                    $http.post('/getAspects/', requestData).then(function(data){
                        $scope.loaded = data.data;
                        console.log($scope.loaded);
                        $scope.loading = false;
                    }, function(data){
                        console.log(data);
                        $scope.loading = false;
                });
                }
            };
        }])
        .controller('FilesController', ['$scope','$http', function($scope, $http){
            $scope.userFiles = [];
            $http.get('/myfiles/').success(function(data) {
                // console.log(data);
                $scope.userFiles = data;
            console.log($scope.userFiles);

            });

        }])
        .controller("TextController", ['$scope', '$http', function($scope, $http) {
            $scope.text = '';
            $scope.loading = false;
            $scope.submit_text = function() {
                console.log($scope.text);
                var requestData = {"text": $scope.text};
                if($scope.text != undefined) {
                    $scope.loading = true;
                    $http.post('/getAspectsOfText/', requestData).then(function(data) {
                        $scope.loaded = data.data;
                        console.log($scope.loaded);
                        $scope.loading = false;
                    }, function(data) {
                        console.log(data);
                        $scope.loading = false;
                    });
                }
            };
        }])
})();