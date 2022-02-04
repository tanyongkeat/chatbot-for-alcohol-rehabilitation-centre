# Multilingual Addaptive Chatbot for Alcohol Rehabilitation Centre
<hr>
It is currently available on https://rehabot.my. <br>

![image](https://user-images.githubusercontent.com/45926191/152497266-2921dfec-a6d5-4afc-b179-15e71041c66b.png)

![image](https://user-images.githubusercontent.com/45926191/152497371-21e191af-7c06-46ff-9a22-27c351e2b9ec.png)


This is the repo for my project, a web-based multiligual adaptive chatbot for an alcohol rehabilitation centre. It is under the collaboration of University Malaya Centre of Addiction Science and Hospital Orang Asli Gombak. It comprises mainly two part:
 - a landing page for users where the user can interact with the chatbot and the information of the stakeholders are shown. 
 - a chatbot management system where the admin can edit the intents and monitor the performance

It aims to automate the process of alcohol risk assessment using AUDIT, and simple alcohol intervention like health education. Besides, the users can also ask general questions about the alcohol common knowledge and the rehab program.

AUDIT assessment: <br>
<img src='https://user-images.githubusercontent.com/45926191/152496105-3ff147b4-896e-40b7-b53c-bdb4fdecb6f3.png' style='width:300px;display:block;'>

For the chatbot to be useful, asking questions in the process of assessment is possible, just like the user is with a clinic personnel. They can continue their assessmnet conveniently by clicking on the top left button. <br>
<img src='https://user-images.githubusercontent.com/45926191/152496619-e857b00e-9b3f-42de-9c84-6c83046efb3d.png' style='width:300px;display:block;'>



### Adaptive capability
The stakeholder doesn't keep a record of commonly asked questions by the users. Currently, the user intents deployed are not based the results of topic modelling on their past enquiries. Rather, the knowledge are extracted from a community handbook provided by the stakeholder. There could be a divergence between the true users' need and the understanding of the developer. As such, the adaptive capability is a must for the long-term sucess of this project. There is a user negative feedback mechanism where the wrong predictions and new intents can be captured and used for retraining of the chatbot later.
<img src='https://user-images.githubusercontent.com/45926191/152493221-4b7cd76c-c0ac-40fa-b1d5-06c415dc5093.png' style='width:600px;display:block;'>
<img src='https://user-images.githubusercontent.com/45926191/152493840-98c92750-4f12-4bff-bd81-5f1636fcb23d.png' style='width:600px;display:block;'>


The retraining of the chatbot can be done on the admin side. 
![image](https://user-images.githubusercontent.com/45926191/152493358-8770dd46-3efb-4350-ad57-824bb7a36b89.png)


The admin can also manage the intents available. Since the responses can be editted, it can be tailored for other rehab center or other applications.
![image](https://user-images.githubusercontent.com/45926191/152494966-d00ad7a7-9878-41ac-a844-1cd6066a1349.png)


In the "Next level selection" part, we can add suggestions of question if the intent is triggered. 
<img src='https://user-images.githubusercontent.com/45926191/152495335-c954674f-3641-4c77-9ebb-d1504ae78b73.png' style='width:350px;display:block;'>



### Multilingual capability
The rich demography of Malaysia would render monolingual approach unfeasible. However the current chatbot development platforms like Dialogflow are not user friendly for multilingual applications where the developer have to maintain one chatbot for each language. This project utilised a pretrained multilingual transformer-based contextual text embedding optimized on sentence similarity task by (Reimer & Gurevych, 2020) for intent detection. There only a single source of training samples needed to be maintained and it can be of mixed languages. 
![image](https://user-images.githubusercontent.com/45926191/152492910-d69e0f6f-c5c5-4689-857f-2b0a8301f4e8.png)


Currently, the languages understood by the chatbot are English, Malay, Tamil, and Mandarin. However, based on the setting, the chatbot only reply in English and Malay. Even if the training samples are only in one language, the alligned multilingual embedding makes it possible for the chatbot to understand questions in different languages.
<br>
<img src='https://user-images.githubusercontent.com/45926191/152492671-e9a7017a-7ec5-44d1-a819-8397e2493652.png' style='width:600px;display:block;'>
<br>

This can be changed by the admin in the setting page. 
![image](https://user-images.githubusercontent.com/45926191/152493093-d0727f1f-1852-40b7-aea2-c87be3aad48e.png)

If the user asked in languages not set to supported in the setting, the chatbot can still understand it, but it will return the answer in the primary language set by the admin. For example, if the primary languages is set to Malay. 
<br>
<img src='https://user-images.githubusercontent.com/45926191/152493737-94dc8174-71d9-4078-b7db-eade5999acda.png' style='width:750px;display:block;'>
<br>


