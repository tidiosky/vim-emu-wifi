// Copyright (c) 2018 by Paderborn University
// (manuel@peuster.de)
// ALL RIGHTS RESERVED.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// Neither the name of the OSM, Paderborn University
// nor the names of its contributors may be used to endorse or promote
// products derived from this software without specific prior written
// permission.

properties([
    parameters([
        string(defaultValue: env.BRANCH_NAME, description: '', name: 'GERRIT_BRANCH'),
        string(defaultValue: 'osm/vim-emu', description: '', name: 'GERRIT_PROJECT'),
        string(defaultValue: env.GERRIT_REFSPEC, description: '', name: 'GERRIT_REFSPEC'),
        string(defaultValue: env.GERRIT_PATCHSET_REVISION, description: '', name: 'GERRIT_PATCHSET_REVISION'),
        string(defaultValue: 'https://osm.etsi.org/gerrit', description: '', name: 'PROJECT_URL_PREFIX'),
        booleanParam(defaultValue: false, description: '', name: 'TEST_INSTALL'),
        string(defaultValue: 'artifactory-osm', description: '', name: 'ARTIFACTORY_SERVER'),
    ])
])

def devops_checkout() {
    dir('devops') {
        git url: "${PROJECT_URL_PREFIX}/osm/devops", branch: params.GERRIT_BRANCH
    }
}


node('docker') {
    checkout scm
    devops_checkout()

    // call the normal OSM devops jobs (without root rights)
    docker_args = ""
    ci_helper = load "devops/jenkins/ci-pipelines/ci_stage_2.groovy"
    ci_helper.ci_pipeline( 'vim-emu',
                           params.PROJECT_URL_PREFIX,
                           params.GERRIT_PROJECT,
                           params.GERRIT_BRANCH,
                           params.GERRIT_REFSPEC,
                           params.GERRIT_PATCHSET_REVISION,
                           params.TEST_INSTALL,
                           params.ARTIFACTORY_SERVER,
                           docker_args)

    // custom test stage that executes vim-emu's unit tests as root
    stage("Post-Test") {
        sh "docker images"
        sh "docker run --rm osm/vim-emu-master ls -l"
        sh "docker run --rm --privileged --pid='host' -u 0:0 -v /var/run/docker.sock:/var/run/docker.sock osm/vim-emu-master pytest -v"
        sh "docker run --rm --privileged --pid='host' -v /var/run/docker.sock:/var/run/docker.sock osm/vim-emu-master flake8 --exclude=.eggs,devopsi,build,examples/charms --ignore=E501,W605,W504 ."
        sh "echo 'done'"
    }
}
