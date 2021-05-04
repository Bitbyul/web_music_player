var Visualizer = function() {
  this.file = null, //the current file
    this.fileparam = null,
    this.fileName = null, //the current file name
    this.audioContext = null,
    this.source = null, //the audio source
    this.info = document.getElementById('info').innerHTML, //this used to upgrade the UI information
    this.infoUpdateId = null, //to sotore the setTimeout ID and clear the interval
    this.animationId = null,
    this.status = 0, //flag for sound is playing 1 or stopped 0
    this.forceStop = false,
    this.allCapsReachBottom = false
};


Visualizer.prototype = {
  ini: function() {
    this._prepareAPI();
    //this._addEventListner();
  },
  play: function(fileparam) {
    var that = this;
    that.fileparam = fileparam;
    that._start();
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
  /*
    _addEventListner: function() {
        var that = this,
            btn_start = document.getElementById('btn_start'),
            dropContainer = document.getElementsByTagName("canvas")[0];
        //listen the file upload
        btn_start.onclick = function() {
            that._updateInfo('Uploading', true);
            //once the file is ready,start the visualizer
            that._start();
        };
        
    },
  */
  _start: function() {
    //read and decode the file into audio array buffer 
    var that = this;

    var request = new XMLHttpRequest();
    
    that.audioContext = new AudioContext();
    
    var audioLoadStart = new Date();

    request.open('POST', "/get/mediafile", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    request.responseType = 'arraybuffer';
    request.onload = function(e) {
      var fileResult = request.response;
      var audioContext = that.audioContext;

      if (audioContext === null) {
        return;
      };
      that._updateInfo('Decoding the audio', true);
      audioContext.decodeAudioData(fileResult, function(buffer) {
        that._updateInfo('Decode succussfully,start the visualizer', true);
        that._visualize(audioContext, buffer, audioLoadStart);
      }, function(e) {
        that._updateInfo('!Fail to decode the file', false);
        console.log(e);
      });
    };
    //assign the file to the reader
    this._updateInfo('Starting read the file', true);
    console.log('p='+that.fileparam);
    request.send('p='+that.fileparam);
  },
  _visualize: function(audioContext, buffer, audioLoadStart) {
    var audioBufferSouceNode = audioContext.createBufferSource(),
      max_time = document.getElementById('max_time'),
      analyser = audioContext.createAnalyser(),
      that = this;
    
    max_time.innerText = parseInt(buffer.duration / 60) + ":" + (parseInt(buffer.duration) % 60);
    
    audioBufferSouceNode.start(0);
    
    var audioLoadOffset = (new Date() - audioLoadStart) / 1000;
    //connect the source to the analyser
    audioBufferSouceNode.connect(analyser);
    //connect the analyser to the destination(the speaker), or we won't hear the sound
    analyser.connect(audioContext.destination);
    //then assign the buffer to the buffer source node
    audioBufferSouceNode.buffer = buffer;
    //play the source
    if (!audioBufferSouceNode.start) {
      audioBufferSouceNode.start = audioBufferSouceNode.noteOn //in old browsers use noteOn method
      audioBufferSouceNode.stop = audioBufferSouceNode.noteOff //in old browsers use noteOn method
    };
    //stop the previous sound if any
    if (this.animationId !== null) {
      cancelAnimationFrame(this.animationId);
    }
    if (this.source !== null) {
      this.source.stop(0);
    }
    //audioBufferSouceNode.start(0);
    this.status = 1;
    this.source = audioBufferSouceNode;
    audioBufferSouceNode.onended = function() {
      that._audioEnd(that);
    };
    this._updateInfo('Playing<br>' + this.fileName, false);
    this.info = 'Playing<br>' + this.fileName;
    this._drawSpectrum(audioContext, audioBufferSouceNode, audioLoadOffset, analyser);
  },
  _drawSpectrum: function(audioContext, audioBufferSouceNode, audioLoadOffset, analyser) {
    var that = this,
      monoL = document.getElementById('mono-L'),
      monoR = document.getElementById('mono-R'),
      current_time = document.getElementById('current_time'),
      seekbar = document.getElementById('seekbar'),
      cwidth = monoL.width,
      cheight = monoL.height - 2,
      meterWidth = 2, //width of the meters in the spectrum
      gap = 0.1, //gap between meters
      capHeight = 2,
      capStyle = '#fff',
      meterNum = 40 * (2 + 2), //count of the meters
      capYPositionArray = []; ////store the vertical position of hte caps for the preivous frame
    
    ctx = monoL.getContext('2d'),
      ctx1 = monoR.getContext('2d'),
      gradient = ctx.createLinearGradient(0, 0, 0, 300);
    gradient2 = ctx1.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(1, '#9331CB');
    gradient.addColorStop(0.5, '#0CD7FD');
    gradient.addColorStop(0, '#f00');


    gradient2.addColorStop(1, '#9331CB');
    gradient2.addColorStop(0.5, '#0CD7FD');
    gradient2.addColorStop(0, '#f00');
    var drawMeter = function() {
      current_time.innerText = parseInt((audioContext.currentTime-audioLoadOffset) / 60) + ":" + (parseInt(audioContext.currentTime-audioLoadOffset) % 60);
      seekbar.value = ((audioContext.currentTime-audioLoadOffset) / audioBufferSouceNode.buffer.duration) * 100;
      
      var array = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(array);
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
          ctx1.fillRect(i * 12, cheight - (--capYPositionArray[i]), meterWidth, capHeight);
        } else {
          ctx.fillRect(i * 12, cheight - value, meterWidth, capHeight);
          ctx1.fillRect(i * 12, cheight - value, meterWidth, capHeight);
          capYPositionArray[i] = value;
        };
        ctx.fillStyle = gradient; //set the filllStyle to gradient for a better look
        ctx.fillRect(i * 12 /*meterWidth+gap*/ , cheight - value + capHeight, meterWidth, cheight); //the meter
        ctx1.fillRect(i * 12 /*meterWidth+gap*/ , cheight - value + capHeight, meterWidth, cheight); //the meter
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
    var text = 'HTML5 Audio Spectrum Visualizer - Alexandre Juca';
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
  }
}