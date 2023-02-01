var Words;
var Usersay;
var Botsay;
var TalkWords;
var Suggestions;
var TaskHints;
var fishNormal_ImageUrl = "/static/image/expression/normal/normal1.gif";
var fishExpression_ImageUrl = "/static/image/expression/";
var starPng_ImageUrl = "/static/image/star.png";
var typingGif_ImageUrl = "/static/image/typing.gif";
var TrainingRoom_ImageUrl = "../static/image/Background/TrainingRoom.jpg";
var PlayingRoom_ImageUrl = "../static/image/Background/PlayingRoom.jpg";
var Book_ImageFileUrl = "../static/image/story_img/";
var res_data;
var random_pitch;
var voices = [];
var voicesID = 1;
var handler = { "name" : "input_userId" }; 
var intent = { "params" : {}, "query" : "" }; 
var scene = { "name" : "input_userId" };  
var session = { "id": GenerateRandom(), "params" : {} }; 
var user = { "lastSeenTime" : "", "character" : "fish_teacher", "player" : 1 }; 
// var user = { "lastSeenTime" : "", "character" : "fish_classmate" }; 
var chatbotWords = [];
var chatbotWords_speech = [];
var chatbotWords_delay = [];
var chatbotWords_expression = "happy";
var chatbotWords_last = "";
var usersay_last= "";
var sync_waitInput_flag = 0;
var rec_imageUrl = "";
var post_count = 0;
var suggest_arr = ["501", "502", "503", "504", "505", "506"];
var score = 0;
var suggest_exist = 0;
// 心情變數 PA
var CE_P=0;
var CE_A=0;
var selected_page = []
var toHiddenID = "Character"
var AllTrainContent;
var leaderboardContent;
var rankingIndex;


// 使用者輸入訊息
function user_inputPress() {

	// 按下enter鍵
	if (event.keyCode == 13) { 	
		console.log(TalkWords.value);
		user_sendMsg(Object);
	}	
} 

// 使用者確定發送訊息
function user_sendMsg(Object) {
	// 終止語音
	window.speechSynthesis.cancel();

	// 啟動語音功能
	speech_chatbotTalk(" ");

	// 判斷使用者發送方式
	if(session['params']['NextScene'] == "SQuAD_get_Page" && selected_page.length != 0){
		// 建議文字紐(多選)方式

		// 對已選取的頁數進行排序
		selected_page.sort(function(a, b) {
			return a - b;
		});
		console.log("Page:", selected_page);
		add_userTalk(selected_page);
		TalkWords.value = selected_page;
		selected_page.length = 0;
	}
	else if(Object.value == undefined){
		// 輸入文字方式
		add_userTalk(TalkWords.value);
	}
	else{
		// 建議文字紐方式
		add_userTalk(Object.value);
		TalkWords.value = Object.value;
	}

	send_userJson();

	if(sync_waitInput_flag == 1){
		console.log("sync_waitInput_flag == 1")
		//show_chatbotTyping()
		//同步等待
		setTimeout(function(){
			chatbotWords = [];
    		send_userJson();
    		//clear_chatbotTyping()
		},1000);
	}
	
	show_chatbotTyping();  // 暫時加的
	// 清空輸入值
	TalkWords.value = "";
}

function user_sendPages(Object){
	if(selected_page.includes(Object.value)){
		// 從selected_page中刪除頁數
		console.log("delete", Object.value);
		selected_page.splice(selected_page.indexOf(Object.value), 1);
	}
	else{
		// 新增頁數到selected_page中
		console.log("add", Object.value);
		selected_page.push(Object.value);
	}
}

// 加入使用者對話訊息
function add_userTalk(talk_str){

	//定義使用者輸入為空字串
	var usertalkStr = "";
    var chatbotWords_last_Str="";
	if(talk_str == ""){
		 // 消息為空事件
		alert("請輸入文字訊息");
		clear_suggestList();
		return;
	}
	if(chatbotWords_last != ""){	
	//發言字數偵測	
	if (talk_str.length<5){
		CE_P=CE_P-2
		CE_A=CE_A-1
		}
	else{
		CE_P=CE_P+3
		CE_A=CE_A+1
	}
	
	usertalkStr = '<div class="user local"><div class="text">' + talk_str +'</div></div>' ; 
	chatbotWords_last_Str =  '<div class="user remote"><div class="text">' + chatbotWords_last +'</div></div>';
	
	// 使用者內容拼接於對話視窗
	//usersay_last = usertalkStr ;
	//Usersay.innerHTML = usertalkStr;	
	Words.innerHTML = Words.innerHTML + chatbotWords_last_Str + usertalkStr;
	Words.scrollTop = Words.scrollHeight;
	chatbotWords_last="";
	}
	// setTimeout(function(){	
 //    	change_chatbotMood()
	// },2000);

	clear_suggestList();
}


// 加入機器人對話訊息
function add_chatbotTalk(){

	var chatbotStr = "";	
	
	if(chatbotWords[0] != ""){

		for(let i = 0; i < chatbotWords.length; i++){
			
			if(chatbotWords_last == chatbotWords[i]){
	            chatbotWords[i] = "";
	            chatbotWords_speech[i] = ""; 
	            break;
          	}	
			if (chatbotWords_last == chatbotWords[i] ){
				chatbotWords[i]= "";
				chatbotWords_speech[i]="";
				console.log("重複清空")
			}
			// 當機器人用SQuAD生成答案時直接pushtext(不需要setTimeout來等待)
			if(session['params']['NextScene'] == 'SQuAD_get_Ans' && session['params']['answerFrom'] == "SQuAD"){
				if(i == 0 ){
					console.log("i=0")							
					pushtext(i);
				}
				else if(i == (chatbotWords.length-1)){
					console.log("i=last");
					console.log("ㄇ我在這")	;	
					// 內容發音
					speech_chatbotTalk(chatbotWords_speech[i]);
					// 將機器人文字顯示於上方
					chatbotStr = '<div class="dialog-bottom"><div class="top">' + chatbotWords[i] +'</div></div>';
					Botsay.innerHTML = chatbotStr;				
					// 下方補進上一句對話框								
					chatbotWords_last = chatbotWords[i];
				}
				else{
					console.log("i=else");
					pushtext(i);
				}
			}
			else{
				if(i == 0){
					console.log("i=0");
					setTimeout(function(){pushtext(i)},1500);
					/*
					// 內容發音
					speech_chatbotTalk(chatbotWords_speech[i]);
					// 將機器人文字顯示於上方
					chatbotStr = '<div class="dialog-bottom"><div class="top">' + chatbotWords[i] +'</div></div>';
					Botsay.innerHTML = chatbotStr;				
					// 下方補進上一句對話框				
					if(chatbotWords_last!=""){
					chatbotWords_last_Str =  '<div class="user remote"><div class="text">' + chatbotWords_last +'</div></div>';
					Words.innerHTML = Words.innerHTML + chatbotWords_last_Str  ;
					Words.scrollTop = Words.scrollHeight;
					}
					chatbotWords_last = chatbotWords[i]
					*/
				}
				else if(i == (chatbotWords.length-1)){
					console.log("i=last")
					setTimeout(function(){
						console.log("ㄇ我在這")		
						// 內容發音
						speech_chatbotTalk(chatbotWords_speech[i]);
						// 將機器人文字顯示於上方
						chatbotStr = '<div class="dialog-bottom"><div class="top">' + chatbotWords[i] +'</div></div>';
						Botsay.innerHTML = chatbotStr;				
						// 下方補進上一句對話框								
						chatbotWords_last = chatbotWords[i]
						},i*7000)
						
					
					}
				else{
					console.log("i=else")
					setTimeout(function(){pushtext(i)},i*6000)
				}
			}

		}

			
	
	}
};
function pushtext(N){
	if (chatbotWords_last == chatbotWords[N] ){
		chatbotWords[N]= "";
		chatbotWords_speech[N]="";
		console.log("重複清空");
		// setTimeout(function(){show_chatbotTyping();},100)  // 暫時註解
	}
	// show_chatbotTyping()	// 暫時註解										
	// 內容發音
	speech_chatbotTalk(chatbotWords_speech[N]);
	// 將機器人文字顯示於上方
	chatbotStr = '<div class="dialog-bottom"><div class="top">' + chatbotWords[N] +'</div></div>';
	Botsay.innerHTML = chatbotStr;				
	// 下方補進上一句對話框				
	if(chatbotWords_last!=""){
	chatbotWords_last_Str =  '<div class="user remote"><div class="text">' + chatbotWords_last +'</div></div>';
	Words.innerHTML = Words.innerHTML + chatbotWords_last_Str  ;
	Words.scrollTop = Words.scrollHeight;
	}
	chatbotWords_last = chatbotWords[N]
}




function sleep(ms) {
  return new Promise(resolveFunc => setTimeout(resolveFunc, ms));
}
// 非同步延遲 delay(min)
function delay(n){
    return new Promise(function(resolve){setTimeout(resolve, n * 1000);});
}
function syncDelay(milliseconds){
 var start = new Date().getTime();
 var end=0;
 while( (end-start) < milliseconds){
     end = new Date().getTime();
 }
}



///
var synth = window.speechSynthesis;

function setVoices() {
  return new Promise((resolve, reject) => {
  let timer;
  timer = setInterval(() => {
    if(synth.getVoices().length !== 0) {
      resolve(synth.getVoices());
      clearInterval(timer);
    }
  }, 10);
 }) 
}
setVoices().then(data => voices = data);


// 機器人內容發出聲音
function speech_chatbotTalk(chatbotspeechStr){
	
//SpeechSynthesisUtterance.lang：設定或取得發音的語言。
//SpeechSynthesisUtterance.pitch：設定或取得發音的音調。
//SpeechSynthesisUtterance.rate：設定或取得發音的速度。
//SpeechSynthesisUtterance.text：設定或取得發音的文字內容。
//SpeechSynthesisUtterance.voice：設定或取得發音的聲音。
//SpeechSynthesisUtterance.volume：設定或取得發音的音量。	
	
	// console.log(voices);
	var toSpeak = new SpeechSynthesisUtterance(chatbotspeechStr);
		//語速
		toSpeak.rate = 1.5;		
		toSpeak.pitch = 1;      
		//女聲
    	toSpeak.voice = voices[voicesID];
    	//
    	if (CE_P>5){
    		toSpeak.pitch = 1.5; 
    	}
    	else if (CE_P>10 ){
    		toSpeak.pitch = 2.3;
    	}
    	else if (CE_A > 2 ){
    		toSpeak.rate = 1.2;
    	}
    	else if (CE_A > 8 ){
    		toSpeak.rate = 1.4;
    	}
    window.speechSynthesis.speak(toSpeak);
    	
}


// 顯示建議文字紐
function show_suggestList(){
	
	var suggestionStr = "";
	
	if(session["params"]['NextScene'] == 'SQuAD_chatbotName'){
		for(var i = 0; i < suggest_arr.length; i++){
			// 這邊待修改(要把button改成機器人圖片)
			suggestionStr += '<button class="suggest_Btn" onclick="user_sendMsg(this)"  value=' + suggest_arr[i] + ' style="padding:8px;"><img class="robotStyle" src="/static/image/chatbot/' + suggest_arr[i] + '.png"></button>'
		}
	}
	else{
		for(var i = 0; i < suggest_arr.length; i++){
			suggestionStr += '<button class="suggest_Btn" onclick="user_sendMsg(this)"  value=' + suggest_arr[i] + '>' + suggest_arr[i] + '</button>'
		}
	}
	//20210915
	Suggestions.innerHTML = suggestionStr
	document.getElementById("talk_suggest_id").style.visibility = "visible";
	//版行調整
	if($("#talk_input_id").hasClass("talk_input")){
		document.getElementById("talk_input_id").style.marginTop = "0";
	}
	else{
		document.getElementById("talk_input_id").style.marginTop = "0";
	}
	if(session["params"]['NextScene'] == 'SQuAD_chatbotName'){

	}
	
}

// 清除建議文字紐
function clear_suggestList() {
	//20210915
	document.getElementById("talk_suggest_id").style.visibility = "hidden";

	suggest_arr = [];

	//版行調整
	if($("#talk_input_id").hasClass("talk_input")){
		document.getElementById("talk_input_id").style.marginTop = "0";
	}
	else{
		document.getElementById("talk_input_id").style.marginTop = "0";
	}			
}

// 顯示任務提示
function show_taskHint(task){
	
	if(task == 'Time'){
		task = '時間'
	}
	else if(task == 'Location'){
		task = '地點'
	}
	else if(task == 'Affection'){
		task = '心情'
	}
	else if(task == 'Life'){
		task = '生活經驗'
	}

	var taskHintStr = "";

	
	taskHintStr += '<div class = "taskHint">任務提示：輸入內容須包含<font color="#FF0000">' + task + '</font></div>'
	

	TaskHints.innerHTML = TaskHints.innerHTML + taskHintStr

	//版行調整
	if($("#talk_input_id").hasClass("talk_input")){
		document.getElementById("talk_input_id").style.marginTop = "0";
	}
	else{
		document.getElementById("talk_input_id").style.marginTop = "0";
	}
	
}

// 清除任務提示
function clear_taskHint() {

	TaskHints.innerHTML = "";

	if(suggest_exist == 0){
		//版行調整
		if($("#talk_input_id").hasClass("talk_input")){
			document.getElementById("talk_input_id").style.marginTop = "0";
		}
		else{
			document.getElementById("talk_input_id").style.marginTop = "0";
		}		
	}	
}

// 顯示機器人輸入中
function show_chatbotTyping(){
	
	var chatbotStr = '<div class="dialog-bottom"><div class="top">';

	// 如果在等待機器人回答問題時，加入思考通用句
	if(res_data != null){
		if(res_data.hasOwnProperty("scene") && res_data["session"]["params"].hasOwnProperty("thinking_word")){
			if(res_data['scene']['next']['name'] == "SQuAD_get_Ans" && res_data["session"]["params"].hasOwnProperty("thinking_word"))
				if (res_data["session"]["params"]['thinking_word'] != "") {
					chatbotStr += res_data["session"]["params"]['thinking_word'] + '<br>';
				}
		}
	}
	chatbotStr += '<img class="typing" src ='+ typingGif_ImageUrl +' width="50" height="13"></div></div>'
	Botsay.innerHTML = chatbotStr;
	//Words.innerHTML = Words.innerHTML + chatbotStr;
	Words.scrollTop = Words.scrollHeight;	

	
}

// 刪除機器人輸入中
function clear_chatbotTyping(){
	
	var node_len = document.getElementsByClassName('dialog-bottom').length;

	for(var i = 0 ; i < node_len; i++){

		var get_currentNode = document.getElementsByClassName('dialog-bottom')[i];

		// 檢查目前是否存在機器人typing
		if(get_currentNode.getElementsByClassName("typing").length){
			get_currentNode.remove()
			break;
		}
	}
	
}

// 檢查機器人輸入中
function exist_chatbotTyping(){
	
	var node_len = document.getElementsByClassName('user remote').length;

	for(var i = 0 ; i < node_len; i++){

		var get_currentNode = document.getElementsByClassName('user remote')[i];

		// 檢查目前是否存在機器人typing
		if(get_currentNode.getElementsByClassName("typing").length){
			return true
		}
	}
	return false
	
}



// 使用者傳送json
function send_userJson() {

	console.log(post_count)

	post_count++;
	intent["query"] = TalkWords.value;
	user["lastSeenTime"] = getNowFormatDate();
	var postData = { 
		    	"handler": handler, 
		    	"intent": intent, 
		    	"scene": scene, 
		    	"session": session, 
		    	"user": user 
	} 

	$.ajax({
		url: "/talk",
		type: "POST",
		contentType: "application/json", 
		data: JSON.stringify(postData), 
		success: function (data) {
			res_data = data;
			console.log(postData)
			console.log(data)
			analyze_responseData();
		}
	})
}

function analyze_responseData(){

	/* Step1： Respone JSON 處理 */

	// JSON 存在 prompt
	if(res_data.hasOwnProperty("prompt")){
		chatbotWords = [];
    	chatbotWords_speech = [];

		//機器人回應文字
		for(var item_text in res_data["prompt"]["firstSimple"]["text"]){ 		
 		 	chatbotWords[item_text] = res_data["prompt"]["firstSimple"]["text"][item_text]
 		 	chatbotWords_speech[item_text] = res_data["prompt"]["firstSimple"]["speech"][item_text]
 		 	chatbotWords_delay[item_text] = res_data["prompt"]["firstSimple"]["delay"][item_text]

 		 	//console.log(chatbotWords[item_text])
 		}

		//存在推薦圖片	
		if(res_data["prompt"].hasOwnProperty("content")){
		 	rec_imageUrl = res_data["prompt"]["content"]["image"]["url"];
		}
		else{
		 	rec_imageUrl = "";
		}

		//存在分數	
		if(res_data["prompt"].hasOwnProperty("score")){
		 	score += res_data["prompt"]["score"];
		 	console.log(res_data["prompt"]["score"])
		 	show_score();
		}
		else{
		 	score = score;
		}
				 	
	}
	else{
		chatbotWords = [];
    	chatbotWords_speech = []; 
	}

	// JSON 存在 scene 用作場景切換功能
 	if(res_data.hasOwnProperty("scene")){
 	 	handler["name"] = res_data["scene"]["next"]["name"];
 	 	scene["name"] = res_data["scene"]["next"]["name"];
 	}
 	
 	// JSON 存在 session 用作對話存取
 	if(res_data.hasOwnProperty("session")){
 	 	session["params"] = Object.assign(session["params"], res_data["session"]["params"]);
 	}

 	// JSON 存在 suggestions 用作建議輸入文字
	if(res_data["prompt"].hasOwnProperty("suggestions") && res_data["prompt"]["suggestions"].length != 0){
		suggest_arr = [];
		clear_suggestList();
		for(var item_suggest in res_data["prompt"]["suggestions"]){ 		
 		 	suggest_arr[item_suggest] = res_data["prompt"]["suggestions"][item_suggest]["title"]
 		}
		console.log(res_data["prompt"]["suggestions"])
 		suggest_exist = 1;
		setTimeout(function(){show_suggestList()},2000);
 	}
 	else{
 		suggest_arr = [];
 		suggest_count = 0;
 		suggest_exist = 0;
 		clear_suggestList();
 	}

 	// JSON 存在 task 用作任務提示指定輸入
 	if(res_data.hasOwnProperty("session")){
		if(res_data["session"]["params"].hasOwnProperty("task")){
	 		show_taskHint(res_data["session"]["params"]["task"]);
	 	}
	 	else{
	 		clear_taskHint();
	 	} 
	 }

	

	/* Step2：顯示機器人回應 */
	add_chatbotTalk();

	/* Step3：考慮場景 */
	
	// 判斷顯示輸入框及傳送按鈕
	if (session["params"]['NextScene'] == "SQuAD_gameMode" ||
		session["params"]['NowScene'] == "Prompt_SQuAD" ||
		session["params"]['NowScene'] == "SQuAD_get_Page" ||
		session["params"]['ask_for_Ans'] == true ||
		session["params"]['first_nameChatbot'] == true){
		document.getElementById("talkwords").removeAttribute("disabled");
		document.getElementById("talksend").removeAttribute("disabled");
	}

	// 判斷隱藏輸入框及傳送按鈕
	if (session["params"]['NextScene'] == "SQuAD_Get_ChatbotStyle" ||
		session["params"]['NextScene'] == "Prompt_SQuAD" ||
		(session["params"]['NowScene'] == "SQuAD_get_Ans" && session["params"]['NextScene'] == "SQuAD_get_Type")){
		document.getElementById("talkwords").disabled = "disabled";
		document.getElementById("talksend").disabled = "disabled";
	}
	if(session["params"]['NextScene'] == "SQuAD_gameMode"){
		delete session['params']['game_mode'];
	}
	// 判斷同步等待使用者輸入再觸發一次request傳送
	if (scene["name"] == "check_input" ){
		sync_waitInput_flag = 1;
 	}
 	else{
 		sync_waitInput_flag = 0;
 	}

 	// 判斷不等待使用者輸入直接觸發request傳送
 	console.log("scene name", scene["name"])
	if(scene["name"] == "Prompt_character" || scene["name"] == "Prompt_character_sentiment" || scene["name"] == "Prompt_task"  || scene["name"] == "Prompt_event"  || scene["name"] == "Prompt_action" || scene["name"] == "Prompt_dialog" || scene["name"] == "suggestion"){
		 
		if(exist_chatbotTyping()){
			clear_chatbotTyping()
		}
		//show_chatbotTyping()

		setTimeout(function(){	
    		send_userJson()
    		clear_chatbotTyping()
		},500);
	}


	// 判斷不等待使用者輸入直接觸發request傳送(對話達到指定次數)
	if(res_data.hasOwnProperty("session")){
		if(res_data["session"]["params"].hasOwnProperty("dialog_count")){
			if(res_data["session"]["params"]["dialog_count"] > 2){

				if(exist_chatbotTyping()){
					clear_chatbotTyping()
				}
				//show_chatbotTyping()

				setTimeout(function(){	
	    			send_userJson()
	    			clear_chatbotTyping()
				},500);
			}
		}
	}
	

	// 判斷不等待使用者輸入直接觸發request傳送(書名階段比對失敗)
	if(res_data.hasOwnProperty("session")){
		if(res_data["session"]["params"].hasOwnProperty("User_first_match")){
		 	if(res_data["session"]["params"]["User_first_match"] == true || res_data["session"]["params"]["User_second_check"]== true){
		 		send_userJson();
		 	}
		}	 	
	}
	// 選擇訓練場或競技場後
	if((session["params"]["game_mode"] == "訓練場" && session["params"]['NextScene'] == "Get_bookName") ||
		(session["params"]["game_mode"] == "競技場" && session["params"]['NextScene'] == "Prompt_SQuAD")){
		var robotID = session["params"]['chatbotStyle'];
		// 將魚姐姐圖片轉換成學生自訂的機器人圖片，並顯示右側導覽區和書本頁面區
		document.getElementById("fish").src = "/static/image/chatbot/"+robotID+".png";
		document.getElementById("guide_id").style.display = "flex";
		book.style.display = "none";
		// 切換機器人聲音
		voicesID = 0;

		// 存在問答遊戲模式，切換模式
		console.log("已選擇問答遊戲模式:"+session["params"]["game_mode"]+"，切換遊戲背景");
		var Background_Img = '';
		var Mode_Words = '';
		var WordBG_color = ''
		if (session["params"]["game_mode"] == "訓練場"){
			Background_Img = TrainingRoom_ImageUrl;
			WordBG_color = "#302b40";
		}
		else if (session["params"]["game_mode"] == "競技場"){
			Background_Img = PlayingRoom_ImageUrl;
			WordBG_color = "#00bfbe";
			document.getElementById("menu_id").style.visibility = "hidden";
		}
		var Mode_Words = '<div class="Mode_Words" style="background-color: ' + WordBG_color + ';">'
						+ session["params"]["game_mode"]
						+ '</div>';
		ModeBackground.innerHTML = '<div class="Mode_BGimg" style = "background-image: url('+ Background_Img +');"><center>' + Mode_Words + '</center></div>';
		ModeBackground.innerHTML = Mode_Words;

	}

	// 在左上方顯示書籍封面、右方book區塊顯示書籍頁面
	if(session["params"].hasOwnProperty("User_book") && session["params"]['NowScene'] == "Prompt_SQuAD"){
		// 書本封面
		var bookName = session["params"]["User_book"];
		book.style.display = "block";
		book_cover.style.display = "block"
		book_showPages();
		book_cover.innerHTML = '<img src="' + Book_ImageFileUrl + bookName + '/cover.jpg"></img>';
	}
	
	// 加上頁數的多選按鈕
	if(session['params']['NextScene'] == "SQuAD_get_Page"){
		var allPageImg = '';
		for(let i = 2; i <= 23; i++){
			allPageImg += '<div class="page" id="bookPage' + i + '">';
			allPageImg += '<label><input type="checkbox" onclick="user_sendPages(this)" name="pages" value=' + i + ' /><span class="round button">' + i + '</span></label>';
			allPageImg += '</div>';
		}
		document.getElementById("bookPage_id").innerHTML = allPageImg;
		// document.getElementById("talkwords").style.visibility = "hidden";
		// document.getElementById("talksend").style.visibility = "visible";
		document.getElementById("talkwords").disabled = "disabled"
		document.getElementById("talksend").removeAttribute("disabled");
	}

	//進到下一輪問答時先把頁數的按鈕移除 
	if(session['params']['NowScene'] == "SQuAD_get_Page" && session['params']['NextScene'] == "SQuAD_get_Type"){
		for(let i = 2; i <= 23; i++){
			document.getElementById("bookPage_id").innerHTML = "";
		}
	}
	// 競技場選機器人時，book區顯示所有機器人資訊
	if(session["params"]["game_mode"] == "競技場" && session["params"]['NextScene'] == "Get_bookName"){
		book.style.display = "block";
		var allUserData = session["params"]['allUserData'];
		var allUserData_display = '<table>';
		for(var i = 0; i < allUserData.length; i++){
			allUserData_display += '<tr><td style="text-align: center; width: 30%;"><img src="/static/image/chatbot/' + allUserData[i]['chatbotStyle'] + '.png"></td>';
			allUserData_display += '<td class="botDataInfo"><p class="highlightText">' + allUserData[i]['chatbotName'] + '</p>主人：' + allUserData[i]['User_id'][0] + "班 " + allUserData[i]['User_id'][1] + "號" + '<br>答對率：' + allUserData[i]['score'] + '%</td></tr>';
		}
		allUserData_display += "</table>";
		book.innerHTML = allUserData_display;
		document.getElementById("menu_id").style.visibility = "hidden";
	}
	if(session["params"]["backToMainMenu"] == true){
		delete session['params']['game_mode'];
		delete session['params']['backToMainMenu'];
		book.innerHTML = "";
		book_cover.innerHTML = "";
		book.style.display = "none";
		document.getElementById("guide_id").style.display = "none";
	}

	/* 機器人檔案內容 */
	if(session["params"]['NextScene'] == "Prompt_SQuAD" && session["params"]['game_mode'] == "訓練場"){
		var chatbot_info_display = "";
		var robotID = session["params"]['chatbotStyle'];
		var chatbot_name = '<p class="info_text" id="chatbotFile_botName_id">' + session["params"]['chatbotName'] + '</p>';
		var user_id = '<p class="info_text" id="chatbotFile_userId_id">' + session["params"]['User_id'].replace("_", "班 ") + '號</p>';
		var leaderboardContent = session["params"]['leaderboardContent'];
		var chatbot_score = '';
		for(var i = 0; i < leaderboardContent.length; i ++){
			if(leaderboardContent[i]['User_id'] == session["params"]['User_id']){
				chatbot_score = '<p class="info_text">' + leaderboardContent[i]['score'] + '%</p>';
				break;
			}
		}
		document.getElementById("menu_id").style.visibility = "visible";
		// document.getElementById("trainRecord_content_id").style.visibility = "visible";
		chatbot_info_display += '<img id="bot_style" class="info_img"></img>' + chatbot_name;
		chatbot_info_display += '<img id="user_id" class="info_img" src="/static/image/user-icon.png"></img>' + user_id;
		chatbot_info_display += '<img class="info_img"" src="/static/image/score-icon.png">' + chatbot_score + '</img>'
		
		document.getElementById("chatbotFile_botInfo_id").innerHTML = chatbot_info_display;
		document.getElementById("bot_style").src = "/static/image/chatbot/"+robotID+".png";
	}
	if(session["params"].hasOwnProperty('AllTrainContent') && session["params"]['game_mode'] == "訓練場"){
		console.log("更新訓練日誌、訓練題數排行榜");
		var AllTrainContent = session["params"]['AllTrainContent'];
		var AllTrainCount = session["params"]['AllTrainCount'];
		var rankingIndex = session["params"]['trainRankingIndex'];
		load_trainRecord_content(AllTrainContent);
		load_leaderboard_content(AllTrainCount, rankingIndex, session['params']['User_id'], 'train');
		delete session["params"]['AllTrainContent'];
		delete session["params"]['AllTrainCount'];
		delete session["params"]['trainRankingIndex'];
	}
	if(session["params"].hasOwnProperty('leaderboardContent') && session["params"].hasOwnProperty('testRankingIndex') && session["params"]['game_mode'] == "訓練場"){
		console.log("更新挑戰日誌、競技場排行榜");
		var leaderboardContent = session["params"]['leaderboardContent'];
		var rankingIndex = session["params"]['testRankingIndex'];
		var User_QArecord = session["params"]['User_QArecord'];
		console.log(leaderboardContent)
		load_leaderboard_content(leaderboardContent, rankingIndex, session['params']['User_id'], "test")
		load_testRecord_content(User_QArecord);
		delete session["params"]['leaderboardContent'];
		delete session["params"]['testRankingIndex'];
	}

}

// book頁面顯示
function book_showPages(){
	var bookName = session["params"]["User_book"];
	var OnePageImgUrl = '';
	document.getElementById("book_id").innerHTML = '<div id="bookPage_id" style="width: 300px; height: 1650px; background-size: cover;"></div>';
	OnePageImgUrl = Book_ImageFileUrl + bookName + '/Merge.jpg';
	document.getElementById("bookPage_id").style.backgroundImage = "url('" + OnePageImgUrl + "')";
}


// 改變機器人表情
function change_chatbotMood(){
	var chatbot_mood = document.getElementById("fish").getAttribute("src");
	//console.log(fishExpression_ImageUrl + chatbotWords_expression + "/" + chatbotWords_expression + "1" + ".gif")
   	// /static/image/expression/normal/normal1.gif
    //document.getElementById("fish").src = fishExpression_ImageUrl + chatbotWords_expression + "/" + chatbotWords_expression + "1" + ".gif";
    
    
    if ((parseInt(CE_P/4)< 5) & (parseInt(CE_A/3)<3)) {
    document.getElementById("fish").src = "/static/image/expression/"+ parseInt(CE_P/4)+ parseInt(CE_A/3) +".png"                
    }
    else {
    	CE_P= CE_P -6 ;
    	CE_A= CE_A -4 ;
    }    
             
    
    //setTimeout(function(){
    //    	document.getElementById("fish").src = fishNormal_ImageUrl;
    //    },7000);
}

// 顯示/更新分數
function show_score(){

	var info_content = document.getElementById("info_content_id")
    var info_content_Str = "";

	// 判斷星星圖片有無顯示過
	if (!document.getElementById("score")) {
		// 添加星星圖片與分數於網頁上
		info_content_Str = '<div id="score" >x '+ score +'</div><img id="star" src=' + starPng_ImageUrl + '></img>' ; 
		info_content.innerHTML = info_content.innerHTML + info_content_Str;
	}
	else{
		//更新分數
		document.getElementById("score").textContent = 'x ' + score;
	}
	
}

// 控制導覽區 7 type範例框的顯示
function display_guide(object){
	var example_content = document.getElementById(object.value)

	if(example_content.style.display == "block"){
		example_content.style.display = "none";
	}
	else{
		document.getElementById(toHiddenID).style.display = "none";
		example_content.style.display = "block";
	}
	toHiddenID = object.value
}
function openChatbotFile(){
	document.getElementById("chatbotFile_id").style.display = "block";
}
function cloceChatbotFile(){
	document.getElementById("chatbotFile_id").style.display = "none";
}

function backToMainMenu(){
	handler['name'] = "SQuAD_gameMode";
	delete session['params']['game_mode'];
	document.getElementById("book_id").innerHTML = "";
	document.getElementById("book-cover_id").innerHTML = "";
	document.getElementById("book_id").style.display = "none";
	document.getElementById("guide_id").style.display = "none";
	window.speechSynthesis.cancel();
	cloceChatbotFile();

	send_userJson();
}
// 打開訓練日誌
function openTrainRecord(){
	// 按鈕變化:選擇
	document.getElementById("trainRecordBtn_id").style.background = "#523b6e";
	document.getElementById("trainRecordBtn_id").style.color = "white";
	// 按鈕變化:取消選擇	
	document.getElementById("trainLeaderboardBtn_id").style.background = "#d7dee0";
	document.getElementById("trainLeaderboardBtn_id").style.color = "black";
	document.getElementById("testRecordBtn_id").style.background = "#d7dee0";
	document.getElementById("testRecordBtn_id").style.color = "black";
	document.getElementById("testLeaderboardBtn_id").style.background = "#d7dee0";
	document.getElementById("testLeaderboardBtn_id").style.color = "black";
	// 下方資訊內容變化
	document.getElementById("trainRecord_content_id").style.visibility = "visible";
	document.getElementById("trainLeaderboard_content_id").style.visibility = "hidden";	
	document.getElementById("testRecord_content_id").style.visibility = "hidden";	
	document.getElementById("testLeaderboard_content_id").style.visibility = "hidden";	
}
// 打開訓練題數排行榜
function openTrainLeaderboard(){
	// 按鈕變化:選擇
	document.getElementById("trainLeaderboardBtn_id").style.background = "#523b6e";
	document.getElementById("trainLeaderboardBtn_id").style.color = "white";
	// 按鈕變化:取消選擇	
	document.getElementById("trainRecordBtn_id").style.background = "#d7dee0";
	document.getElementById("trainRecordBtn_id").style.color = "black";
	document.getElementById("testRecordBtn_id").style.background = "#d7dee0";
	document.getElementById("testRecordBtn_id").style.color = "black";
	document.getElementById("testLeaderboardBtn_id").style.background = "#d7dee0";
	document.getElementById("testLeaderboardBtn_id").style.color = "black";
	// 下方資訊內容變化
	document.getElementById("trainRecord_content_id").style.visibility = "hidden";
	document.getElementById("trainLeaderboard_content_id").style.visibility = "visible";	
	document.getElementById("testRecord_content_id").style.visibility = "hidden";	
	document.getElementById("testLeaderboard_content_id").style.visibility = "hidden";	
}
// 打開挑戰日誌
function openTestRecord(){
	// 按鈕變化:選擇
	document.getElementById("testRecordBtn_id").style.background = "#523b6e";
	document.getElementById("testRecordBtn_id").style.color = "white";
	// 按鈕變化:取消選擇
	document.getElementById("trainLeaderboardBtn_id").style.background = "#d7dee0";
	document.getElementById("trainLeaderboardBtn_id").style.color = "black";
	document.getElementById("trainRecordBtn_id").style.background = "#d7dee0";
	document.getElementById("trainRecordBtn_id").style.color = "black";
	document.getElementById("testLeaderboardBtn_id").style.background = "#d7dee0";
	document.getElementById("testLeaderboardBtn_id").style.color = "black";
	// 下方資訊內容變化
	document.getElementById("trainRecord_content_id").style.visibility = "hidden";
	document.getElementById("trainLeaderboard_content_id").style.visibility = "hidden";	
	document.getElementById("testRecord_content_id").style.visibility = "visible";	
	document.getElementById("testLeaderboard_content_id").style.visibility = "hidden";
}
// 打開競技場排行榜
function openTestLeaderboard(){
	// 按鈕變化:選擇
	document.getElementById("testLeaderboardBtn_id").style.background = "#523b6e";
	document.getElementById("testLeaderboardBtn_id").style.color = "white";
	// 按鈕變化:取消選擇	
	document.getElementById("trainRecordBtn_id").style.background = "#d7dee0";
	document.getElementById("trainRecordBtn_id").style.color = "black";
	document.getElementById("trainLeaderboardBtn_id").style.background = "#d7dee0";
	document.getElementById("trainLeaderboardBtn_id").style.color = "black";
	document.getElementById("testRecordBtn_id").style.background = "#d7dee0";
	document.getElementById("testRecordBtn_id").style.color = "black";
	// 下方資訊內容變化
	document.getElementById("trainRecord_content_id").style.visibility = "hidden";
	document.getElementById("trainLeaderboard_content_id").style.visibility = "hidden";	
	document.getElementById("testRecord_content_id").style.visibility = "hidden";	
	document.getElementById("testLeaderboard_content_id").style.visibility = "visible";	
}
// 載入訓練日誌
function load_trainRecord_content(AllTrainContent){
	var AllTrainContent_display = '';
	var index = 0;
	document.getElementById("trainRecord_content_id").innerHTML = '';
	// console.log(AllTrainContent);
	if(AllTrainContent["hits"]["hits"].length == 0){
		AllTrainContent_display = '你還沒有訓練過' + session['params']['chatbotName'] + '喔！';
		document.getElementById("trainRecord_content_id").innerHTML = AllTrainContent_display;
	}
	for(var i = AllTrainContent["hits"]["hits"].length; i > 0; i --){
		index += 1;
		AllTrainContent_display = '';
		AllTrainContent_display += '<div class="chatbotFile_QA"><span class="frame QAbook">書名</span><span>' + AllTrainContent["hits"]["hits"][i-1]["_index"].replace(/_/g, " ") + '</span><br>';
		AllTrainContent_display += '<span class="frame Q">問題</span><span>' + AllTrainContent["hits"]["hits"][i-1]["_source"]["Question"] + '?</span><br>';
		AllTrainContent_display += '<span class="frame A">解答</span><span>' + AllTrainContent["hits"]["hits"][i-1]["_source"]["Answer"] + '</span></div>';
		AllTrainContent_display += '<div class="Num">' + index + '</div>'
		document.getElementById("trainRecord_content_id").innerHTML += AllTrainContent_display + "<hr>";
	}
}
// 載入挑戰日誌
function load_testRecord_content(QAContent){
	document.getElementById("testRecord_content_id").innerHTML = "";
	var display_str = '';
	var challenger = '';
	var content = [];
	var len = 0;
	var score = 0;
	var book_testRecord = {};
	var book_list = ['Ralph the Puppy', 'Birthday Presents', 'My Special Friend', 'Little Donkey', 'Salt and Sugar'];
	var flag = false;
	for(var i = 0; i < book_list.length; i ++){
		if(QAContent.hasOwnProperty(book_list[i])){
			book_testRecord = QAContent[book_list[i]]['test_record'];
			len = Object.keys(book_testRecord).length;
			flag = false;
			for(var j = 0; j < len; j ++){
				challenger = book_testRecord[j]['challenger_id'].replace("_", "班 ") + "號";
				content = book_testRecord[j]['content'];
				if(content.length > 0){
					if(flag == false){ display_str += '<h2>' + book_list[i] + '</h2><br>';}
					flag = true;
					display_str += '<table><tr style="background: #523b6e;"><th>挑戰者 - ' + challenger + '</th>';
					score = Math.round((book_testRecord[j]['correct_count']/content.length)*100);
					display_str += '<th colspan="2">答對率：' + score + '%</th></tr>'; 
					for(var k = 0; k < content.length; k ++){
						if(content[k][1] == null){ content[k][1] = '---';}
						if(content[k][2] == true){ content[k][2] = '<img src="/static/image/right.png">';}
						if(content[k][2] == false){ content[k][2] = '<img src="/static/image/wrong.png">';}
						display_str += '<tr><td class="question" style="border: 0;">' + content[k][0] + '</td>';
						display_str += '<td class="answer" style="border: 0;">' + content[k][1] + '</td>';
						display_str += '<td class="result" style="border: 0;">' + content[k][2] + '</td></tr>';
					}
					display_str += '</table>';

				}
			}
		}
	}
	document.getElementById("testRecord_content_id").innerHTML = display_str;
}
// 載入訓練題數排行榜or競技場排行榜
function load_leaderboard_content(leaderboardContent, rankingIndex, user_id, type){
	var display_str = '';
	score = 0;
	display_str = '<table><tr><th>你的機器人</th><th>你的資訊</th><th>你的名次</th></tr>'
	for(var i = 0; i < rankingIndex.length; i ++){
		if (leaderboardContent[rankingIndex[i]]['User_id'] == user_id){
			display_str += leaderboardContent_display_User(leaderboardContent, rankingIndex, i, false, type);
		}
	}
	display_str += '<tr><td></td><td></td><td></td></tr>'
	display_str += '<tr><th>機器人</th><th>資訊</th><th>名次</th></tr>'
	for(var i = 0; i < rankingIndex.length; i ++){
		if (leaderboardContent[rankingIndex[i]]['User_id'] == user_id){
			display_str += leaderboardContent_display_User(leaderboardContent, rankingIndex, i, true, type);
		}
		else{
			display_str += '<tr><td class="table-center"><img src="/static/image/chatbot/' + leaderboardContent[rankingIndex[i]]['chatbotStyle'] + '.png"></td>';
			display_str += '<td>名稱：' + leaderboardContent[rankingIndex[i]]['chatbotName'] + '<br>主人：' + leaderboardContent[rankingIndex[i]]['User_id'].replace("_", "班 ") + "號";

			if(type == "test"){
				display_str += '<br>答對題數 / 被測驗題數：' + leaderboardContent[rankingIndex[i]]['correct_count_sum'] + ' / ' + leaderboardContent[rankingIndex[i]]['test_count_sum'];
				display_str += '<br>答對率：' + leaderboardContent[rankingIndex[i]]['score'] + "%</td>";
				score = leaderboardContent[rankingIndex[i]]['score'];
			}
			else if(type == "train"){
				display_str += '<br>訓練題數：' + leaderboardContent[rankingIndex[i]]['train_count_sum'] + '</td>';
				score = leaderboardContent[rankingIndex[i]]['train_count_sum'];
			}

			if(score == 0){
				display_str += '<td class="Num table-center"> </td>';
			}
			else{
				if(i < 3){
					display_str += '<td class="Num table-center" style="color:yellow;">' + (i+1) + '</td>';
				}
				else{
					display_str += '<td class="Num table-center">' + (i+1) + '</td>';
				}
			}
		}
	}
	display_str += '</table>'
	if(type == "test"){
		document.getElementById("testLeaderboard_content_id").innerHTML = '';
		document.getElementById("testLeaderboard_content_id").innerHTML = display_str;
	}
	else if(type == "train"){
		document.getElementById("trainLeaderboard_content_id").innerHTML = '';
		document.getElementById("trainLeaderboard_content_id").innerHTML = display_str;
	}
}
function leaderboardContent_display_User(leaderboardContent, rankingIndex, index, detail_info, type){
	display_str = '';
	score = 0;
	display_str += '<tr><td class="table-center highlightBG"><img src="/static/image/chatbot/' + leaderboardContent[rankingIndex[index]]['chatbotStyle'] + '.png"></td>';
	display_str += '<td class="highlightBG">';
	if(detail_info == true){
		display_str += '名稱：' + leaderboardContent[rankingIndex[index]]['chatbotName'] + '<br>主人：' + leaderboardContent[rankingIndex[index]]['User_id'].replace("_", "班 ") + "號<br>";
	}

	if(type == "test"){
		display_str += '答對題數 / 被測驗題數：' + leaderboardContent[rankingIndex[index]]['correct_count_sum'] + ' / ' + leaderboardContent[rankingIndex[index]]['test_count_sum'] + '<br>';
		display_str += '答對率：' + leaderboardContent[rankingIndex[index]]['score'] + '%</td>';
		score = leaderboardContent[rankingIndex[index]]['score'];
	}
	else if(type == "train"){
		display_str += '訓練題數：' + leaderboardContent[rankingIndex[index]]['train_count_sum'] + '</td>';
		score = leaderboardContent[rankingIndex[index]]['train_count_sum'];
	}

	if(score == 0){
		display_str += '<td class="Num table-center highlightBG"> </td>';
	}
	else{
		if(index < 3){
			display_str += '<td class="Num table-center highlightBG" style="color:yellow;">' + (index+1) + '</td>';
		}
		else{
			display_str += '<td class="Num table-center highlightBG">' + (index+1) + '</td>';
		}
	}
	return display_str;
}

// 取得目前時間
function getNowFormatDate() {

    var date = new Date();
    var dateStr = date.getFullYear()
    + '-' + ('0' + (date.getMonth() + 1)).slice(-2)
    + '-' + ('0' + date.getDate()).slice(-2)
    + ' ' + ('0' + date.getHours()).slice(-2)
    + ':' + ('0' + date.getMinutes()).slice(-2)
    + ':' + ('0' + date.getSeconds()).slice(-2)

    return dateStr;
}

// 產生隨機亂數30位元
function GenerateRandom() {
	
	var Random_length = 30; 
	var characters = "0123456789abcdefghijklmnopqrstuvwxyz";
	var seed = "";
	var cnt = 0
	var randomNumber = 0
	while( cnt < Random_length ) {
			cnt ++;
			randomNumber = Math.floor(characters.length * Math.random());
			seed += characters.substring(randomNumber, randomNumber + 1)
	}

	return seed;
}

// 裝置RWD使用
var sUserAgent = navigator.userAgent.toLowerCase();
var bIsIpad = sUserAgent.match(/ipad/i) == "ipad";
var bIsIphoneOs = sUserAgent.match(/iphone os/i) == "iphone os";
var bIsMidp = sUserAgent.match(/midp/i) == "midp";
var bIsUc7 = sUserAgent.match(/rv:1.2.3.4/i) == "rv:1.2.3.4";
var bIsUc = sUserAgent.match(/ucweb/i) == "ucweb";
var bIsAndroid = sUserAgent.match(/android/i) == "android";
var bIsCE = sUserAgent.match(/windows ce/i) == "windows ce";
var bIsWM = sUserAgent.match(/windows mobile/i) == "windows mobile";


window.onload = function(){  
	Usersay = document.getElementById("usersay"); 
	Botsay = document.getElementById("botsay"); 
	Words = document.getElementById("words"); 
	TalkWords = document.getElementById("talkwords");
	TalkSend = document.getElementById("talksend"); 
	Suggestions = document.getElementById("talk_suggest_id"); 
	TaskHints = document.getElementById("talk_taskHint_id"); 
	ModeBackground = document.getElementById("mode_background");
	book = document.getElementById("book_id"); 
	book_cover = document.getElementById("book-cover_id"); 

	// 目前使用裝置
	if (bIsIpad || bIsIphoneOs || bIsMidp || bIsUc7 || bIsUc || bIsAndroid || bIsCE || bIsWM) {
		console.log("手機");  
		document.getElementById('talk_content_id').className = 'talk_content_mob';		
		document.getElementById('words').className = 'talk_show_mob';	
		document.getElementById('talk_input_id').className = 'talk_input_mob';	
		document.getElementById('talkwords').className = 'talk_word_mob';	
		document.getElementById('talk_suggest_id').className = 'talk_suggest_mob';	
		document.getElementById('guide_id').className = 'guide_mob';
		document.getElementById('guide_robot_id').className = 'guide_robot_mob';
		document.getElementById('book_id').className = 'book_mob';
	} else {
		console.log("電腦"); 
		document.getElementById('talk_content_id').className = 'talk_content';
		document.getElementById('words').className = 'talk_show';	
		document.getElementById('talk_input_id').className = 'talk_input';	
		document.getElementById('talkwords').className = 'talk_word';	
		document.getElementById('talk_suggest_id').className = 'talk_suggest';	
		document.getElementById('guide_id').className = 'guide';
		document.getElementById('book_id').className = 'book';
	}

	show_suggestList()

	//random_pitch = (Math.random()*(1.3 - 0.8) + 0.8).toFixed(2) // 產生隨機小數

	
}

