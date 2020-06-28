import axios from 'axios'

export default {
  buildUri({endPoint, classrooms, students, subjects, tokenType}){
    let uris = {
      checkStudent: '/admin/students/' + students, 
      classroomProgression: '/progression/chapters/classrooms/'+ classrooms +'/subjects/'+ subjects,
      studentLastLesson: 'activity/students/' + students + '/subjects/' + subjects + '/last',
      studentConfusion: "/tasks/confusion/students/" + students + "/subjects/" + subjects,
      globalConfusion: "/tasks/confusion/subjects/" + subjects,
      studentInfo: "activity/students/" + students + "/subjects/" + subjects + "/info",
      studentTokens1: subjects + "/" + tokenType + "/students/" + students,
      studentTokens2: subjects + "/" + tokenType + "/students/" + students,
      studentTokens3: subjects + "/" + tokenType + "/students/" + students,
      studentDecision: '/tasks/decision/students/' + students + '/subjects/' + subjects,
    }
    return uris[endPoint]
    },


  getData(uri){
    
    return axios.get(uri, { validateStatus: false})
    .then(response => {
      if (response.status == 404){
        this.status = "error"
        this.response = false
        this.message = response.data.message
        console.log("getDATA", uri,":", response.status, "DATA:", response.data, "MSG:", response.data.message);
        // return [this.response, this.message, this.status]
        // return [false, response, response.data.msg]
        return [false, response.data.message, "error"]
      }
      else if (response.status == 406){
        this.status = "error"
        this.response = false
        this.message = response.data.message
        console.log("getDATA", uri,":", response.status, "DATA:", response.data, "MSG:", response.data.message);
        // console.log(uri, response.status, response.data);
        // return [this.response, this.message, this.status]
        return [false, response.data, "error"]
      }
      else if (response.status == 500){
        this.status = "error"
        this.response = false
        this.message = response.data
        
        // console.log(uri, response.status, response.data);
        console.log("getDATA", uri,":", response.status, "DATA:", response.data, "MSG:", response.data.message);
        return [false, response.data, "error"]
        // return [false, response]
      }
      else {
        this.status = "ready"
        this.response = true
        this.data = response.data
        // console.log(uri, response.status, response.data);
        console.log("getDATA", uri, ":", response.status, "DATA:", response.data);
        return [true, response.data, "ready"]
        // return [true, response]
      }
    })
    
  },

}