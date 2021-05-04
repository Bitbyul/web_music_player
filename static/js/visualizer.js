var Visualizer = function() {
  this.file = null, //the current file
    this.fileparam = null,
    this.audioEle = null,
    this.audioContext = null,
    this.source = null,
    this.info = document.getElementById('info').innerHTML, //this used to upgrade the UI information
    this.infoUpdateId = null, //to sotore the setTimeout ID and clear the interval
    this.animationId = null,
    this.status = 0, //flag for sound is playing 1 or stopped 0
    this.forceStop = false,
    this.allCapsReachBottom = false,
    this.lyric = null
};


Visualizer.prototype = {
  ini: function() {
    this._prepareAPI();
  },
  play: function(fileparam) {
    this.fileparam = fileparam;
    this.lyric = null
    this._start();
  },
  suspend: function() {
    this._suspend();
  },
  resume: function() {
    this._resume();
  },
  endCallBack: function(f) {
    this._endCallBack = f;
  },
  setLyric: function(d) {
    this.lyric = d;
  },
  _prepareAPI: function() {
    //fix browser vender for AudioContext and requestAnimationFrame
    window.AudioContext = window.AudioContext || window.webkitAudioContext || window.mozAudioContext || window.msAudioContext;
    window.requestAnimationFrame = window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.msRequestAnimationFrame;
    window.cancelAnimationFrame = window.cancelAnimationFrame || window.webkitCancelAnimationFrame || window.mozCancelAnimationFrame || window.msCancelAnimationFrame;
    try {
    } catch (e) {
      this._updateInfo('!Your browser does not support AudioContext', false);
      console.log(e);
    }
  },
  _suspend: function() {
    this.audioEle.pause();
    this.audioContext.suspend();
  },
  _resume: function() {
    this.audioContext.resume();
    this.audioEle.play();
  },
  _start: function() {
    
    if (this.source !== null) {
      this._suspend();//.source.stop(0);
      this.source.disconnect();
      this.audioContext.close();
    }
    
    this.audioContext = new AudioContext();

    const audioEle = new Audio();
    
    
    audioEle.src = '/get/mediafile?p='+this.fileparam;//insert file name here
    audioEle.autoplay = true;
    audioEle.preload = 'metadata';
    audioEle.addEventListener("loadedmetadata", function(_event) {
        document.getElementById('max_time').innerText = parseInt(audioEle.duration / 60) + ":" + (parseInt(audioEle.duration) % 60);
    });
    
    this.audioEle = audioEle;
    
    this._visualize(this.audioContext);
    //assign the file to the reader
    this._updateInfo('Starting read the file', true);
    console.log('p='+this.fileparam);
  },
  _visualize: function(audioContext) {
    var audioSourceNode = this.audioContext.createMediaElementSource(this.audioEle),
      analyser = audioContext.createAnalyser(),
      that = this;
    
    //connect the source to the analyser
    audioSourceNode.connect(analyser);
    //connect the analyser to the destination(the speaker), or we won't hear the sound
    analyser.connect(audioContext.destination);
    
    //play the source
    //stop the previous sound if any
    if (this.animationId !== null) {
      cancelAnimationFrame(this.animationId);
    }
    //audioBufferSouceNode.start(0);
    this.status = 1;
    this.source = audioSourceNode;
    this.audioEle.onended = function() {
      that._audioEnd(that);
      that._endCallBack();
    };
    this._updateInfo('Playing<br>' + this.fileName, false);
    this.info = 'Playing<br>' + this.fileName;
    this._drawSpectrum(analyser);
  },
  _drawSpectrum: function(analyser) {
    var that = this,
      monoL = document.getElementById('mono-L'),
      monoR = document.getElementById('mono-R'),
      current_time = document.getElementById('current_time'),
      seekbar = document.getElementById('seekbar'),
      lyrics_prev = document.getElementById('lyrics-prev'),
      lyrics_now = document.getElementById('lyrics-now'),
      lyrics_next = document.getElementById('lyrics-next'),
      lyric_index = -1,
      cwidth = monoL.width,
      cheight = monoL.height - 2,
      meterWidth = 1.5, //width of the meters in the spectrum
      gap = 0.1, //gap between meters
      capHeight = 2,
      capStyle = '#fff',
      meterNum = 40 * (2 + 2), //count of the meters
      capYPositionArray = []; ////store the vertical position of hte caps for the preivous frame
    
    lyrics_prev.innerText = "-";
    lyrics_now.innerText = "-";
    lyrics_next.innerText = "-";
    
    ctx = monoL.getContext('2d'),
      ctx1 = monoR.getContext('2d'),
      gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient2 = ctx1.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(1, 'rgb(147, 49, 203)'); // #9331CB
    gradient.addColorStop(0.5, 'rgb(12, 215, 253)'); // #0CD7FD
    gradient.addColorStop(0, 'rgb(255, 0, 0)'); // #f00

    gradient2.addColorStop(0, 'rgba(147, 49, 203, 0.8)');
    gradient2.addColorStop(0.5, 'rgba(12, 215, 253, 0)');
    //gradient2.addColorStop(1, 'rgba(255, 0, 0, 1)');
    //gradient2.addColorStop(0, '#f00');
    var drawMeter = function() {
      current_time.innerText = parseInt((that.audioEle.currentTime) / 60) + ":" + (parseInt(that.audioEle.currentTime) % 60);
      seekbar.value = ((that.audioEle.currentTime) / that.audioEle.duration) * 100;
      
      if(that.lyric!=null) {
        if(lyric_index==-1){
          lyrics_next.innerText = that.lyric[0]['d']
          lyric_index = 0;
        }
        for(i=lyric_index;;i++)
          try{
            if(that.lyric[i]['t'] > that.audioEle.currentTime){
              lyric_index = i;
              break;
            }else{
              lyrics_prev.innerText = lyrics_now.innerText;
              lyrics_now.innerText = lyrics_next.innerText;
              lyrics_next.innerText = that.lyric[lyric_index+1]['d']
            }
          }catch (e){
            lyrics_next.innerText = "-";
            that.lyric = null;
            break;
          }
      }
      
      
      var array = new Uint8Array(analyser.frequencyBinCount);//new Uint8Array(analyser.fftSize);
      analyser.getByteFrequencyData(array);//getByteTimeDomainData(array);
      //for( var i=920; i< array.length; i++){
      //  array[i] = 0;
      //}
      //array = array.slice(300,800); // 300, 800
      /*
      for(var i=0; i<array.length; i++){
        if(array[i] < 130) array[i] = 0;
        else array[i] -= 100;
      }
      */
      if (that.status === 0) {
        //fix when some sounds end the value still not back to zero
        for (var i = array.length - 1; i >= 0; i--) {
          array[i] = 0;
        };
        allCapsReachBottom = true;
        for (var i = capYPositionArray.length - 1; i >= 0; i--) {
          allCapsReachBottom = allCapsReachBottom && (capYPositionArray[i] === 0);
        };
        if (allCapsReachBottom) {
          cancelAnimationFrame(that.animationId); //since the sound is top and animation finished, stop the requestAnimation to prevent potential memory leak,THIS IS VERY IMPORTANT!
          return;
        };
      };
      
      
      var step = Math.round(array.length / meterNum); //sample limited data from the total array
      ctx.clearRect(0, 0, cwidth, cheight);
      ctx1.clearRect(0, 0, cwidth, cheight);
      for (var i = 0; i < meterNum; i++) {
        var value = array[i * step];
        if (capYPositionArray.length < Math.round(meterNum)) {
          capYPositionArray.push(value);
        };
        ctx.fillStyle = capStyle;
        ctx1.fillStyle = capStyle;
        //draw the cap, with transition effect
        if (value < capYPositionArray[i]) {
          ctx.fillRect(i * 12, cheight - (--capYPositionArray[i]), meterWidth, capHeight);
          //ctx1.fillRect(i * 12, cheight - (--capYPositionArray[i]), meterWidth, capHeight);
        } else {
          ctx.fillRect(i * 12, cheight - value, meterWidth, capHeight);
          //ctx1.fillRect(i * 12, cheight - value, meterWidth, capHeight);
          capYPositionArray[i] = value;
        };
        ctx.fillStyle = gradient; //set the filllStyle to gradient for a better look
        ctx1.fillStyle = gradient2;
        ctx.fillRect(i * 12 /*meterWidth+gap*/ , cheight - value + capHeight, meterWidth, cheight); //the meter
        ctx1.fillRect(i * 12 /*meterWidth+gap*/ , 0, meterWidth, 0 + value - capHeight); //the meter
      }
      that.animationId = requestAnimationFrame(drawMeter);
    }
    this.animationId = requestAnimationFrame(drawMeter);
  },
  _audioEnd: function(instance) {
    if (this.forceStop) {
      this.forceStop = false;
      this.status = 1;
      return;
    };
    this.status = 0;
    var text = 'END';
    document.getElementById('info').innerHTML = text;
    instance.info = text;
  },
  _updateInfo: function(text, processing) {
    var infoBar = document.getElementById('info'),
      dots = '...',
      i = 0,
      that = this;
    infoBar.innerHTML = text + dots.substring(0, i++);
    if (this.infoUpdateId !== null) {
      clearTimeout(this.infoUpdateId);
    };
    if (processing) {
      //animate dots at the end of the info text
      var animateDot = function() {
        if (i > 3) {
          i = 0
        };
        infoBar.innerHTML = text + dots.substring(0, i++);
        that.infoUpdateId = setTimeout(animateDot, 250);
      }
      this.infoUpdateId = setTimeout(animateDot, 250);
    };
  },
  _endCallBack : function(){}
}