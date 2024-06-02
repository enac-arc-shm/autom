import MdiFont from "https://esm.sh/@mdi/font";
document.querySelectorAll("#sidebar > ul > li").forEach( function(li, index) {
	//console.log(li);
	li.addEventListener('click',function(e){
		//console.log(e);
		var drpdown = li.querySelector('.dropdown');
		if(drpdown.classList.contains('active')){
			li.classList.remove('active');
			drpdown.classList.remove('active');
			hide(drpdown);
		}
		else
		{
			drpdown.classList.add('active');
			li.classList.add('active');
			show(drpdown);
		}
	})	
});

import MdiFont from "https://esm.sh/@mdi/font";
document.querySelectorAll("#sidebar > ul > li").forEach( function(li, index) {
	//console.log(li);
	li.addEventListener('click',function(e){
		//console.log(e);
		var drpdown = li.querySelector('.dropdown');
		if(drpdown.classList.contains('active')){
			li.classList.remove('active');
			drpdown.classList.remove('active');
			hide(drpdown);
		}
		else
		{
			drpdown.classList.add('active');
			li.classList.add('active');
			show(drpdown);
		}
	})	
});