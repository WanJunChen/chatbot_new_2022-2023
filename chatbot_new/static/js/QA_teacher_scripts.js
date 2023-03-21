
var time = 20;
var refresh_count = 0
setInterval(function(){
    
    $.getJSON('http://qachatbot.cosci.tw/QAchatbot/leaderboard_data', function(data) {
        refresh_count += 1;
        console.log("刷新" + refresh_count, data)
        time = 20;

        var train_leaderboard = data['train_leaderboard'];
        var test_leaderboard = data['test_leaderboard']

        load_leaderboard_content(train_leaderboard['leaderboardContent'], train_leaderboard['RankingIndex'], 'train');
        load_leaderboard_content(test_leaderboard['leaderboardContent'], test_leaderboard['RankingIndex'], "test")
    });
}, 20000);

showTime();
function showTime()
{
    document.getElementById('refresh_time_id').innerHTML= time+" 秒後  刷新排行榜";
    
    time -= 1;
    // if(time == 0){
    //     time = 20;
    // }
    //每秒執行一次,showTime()
    setTimeout("showTime()",1000);
}

// 載入訓練題數排行榜or競技場排行榜
function load_leaderboard_content(leaderboardContent, rankingIndex, type){
	var display_str = '';
	score = 0;
	display_str = '<table><tr><td></td><td></td><td></td></tr>'
	display_str += '<tr><th>機器人</th><th>資訊</th><th>名次</th></tr>'
	for(var i = 0; i < rankingIndex.length; i ++){
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