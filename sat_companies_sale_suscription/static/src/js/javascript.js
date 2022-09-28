odoo.define('sat_companies_sale_suscription.javascript', ['web.ajax'], function(require){

    "use strict";
  
    var ajax = require('web.ajax');
    var id_sale = document.getElementById("id_value_sale").textContent;
    
    //SIGNATURE PAD JQUERY
    (function() {
      window.requestAnimFrame = (function(callback) {
        return window.requestAnimationFrame ||
          window.webkitRequestAnimationFrame ||
          window.mozRequestAnimationFrame ||
          window.oRequestAnimationFrame ||
          window.msRequestAnimaitonFrame ||
          function(callback) {
            window.setTimeout(callback, 1000 / 60);
          };
      })();
    
      var canvas = document.getElementById("sig-canvas");
      var ctx = canvas.getContext("2d");
      ctx.strokeStyle = "#222222";
      ctx.lineWidth = 4;
    
      var drawing = false;
      var mousePos = {
        x: 0,
        y: 0
      };
      var lastPos = mousePos;
    
      canvas.addEventListener("mousedown", function(e) {
        drawing = true;
        lastPos = getMousePos(canvas, e);
      }, false);
    
      canvas.addEventListener("mouseup", function(e) {
        drawing = false;
      }, false);
    
      canvas.addEventListener("mousemove", function(e) {
        mousePos = getMousePos(canvas, e);
      }, false);
    
      // Add touch event support for mobile
      canvas.addEventListener("touchstart", function(e) {
    
      }, false);
    
      canvas.addEventListener("touchmove", function(e) {
        var touch = e.touches[0];
        var me = new MouseEvent("mousemove", {
          clientX: touch.clientX,
          clientY: touch.clientY
        });
        canvas.dispatchEvent(me);
      }, false);
    
      canvas.addEventListener("touchstart", function(e) {
        mousePos = getTouchPos(canvas, e);
        var touch = e.touches[0];
        var me = new MouseEvent("mousedown", {
          clientX: touch.clientX,
          clientY: touch.clientY
        });
        canvas.dispatchEvent(me);
      }, false);
    
      canvas.addEventListener("touchend", function(e) {
        var me = new MouseEvent("mouseup", {});
        canvas.dispatchEvent(me);
      }, false);
    
      function getMousePos(canvasDom, mouseEvent) {
        var rect = canvasDom.getBoundingClientRect();
        return {
          x: mouseEvent.clientX - rect.left,
          y: mouseEvent.clientY - rect.top
        }
      }
    
      function getTouchPos(canvasDom, touchEvent) {
        var rect = canvasDom.getBoundingClientRect();
        return {
          x: touchEvent.touches[0].clientX - rect.left,
          y: touchEvent.touches[0].clientY - rect.top
        }
      }
    
      function renderCanvas() {
        if (drawing) {
          ctx.moveTo(lastPos.x, lastPos.y);
          ctx.lineTo(mousePos.x, mousePos.y);
          ctx.stroke();
          lastPos = mousePos;
        }
      }
    
      // Prevent scrolling when touching the canvas
      document.body.addEventListener("touchstart", function(e) {
        if (e.target == canvas) {
          e.preventDefault();
        }
      }, false);
      document.body.addEventListener("touchend", function(e) {
        if (e.target == canvas) {
          e.preventDefault();
        }
      }, false);
      document.body.addEventListener("touchmove", function(e) {
        if (e.target == canvas) {
          e.preventDefault();
        }
      }, false);
    
      (function drawLoop() {
        requestAnimFrame(drawLoop);
        renderCanvas();
      })();
    
      function clearCanvas() {
        canvas.width = canvas.width;
      }
    
      // Set up the UI
      var sigText = document.getElementById("sig-dataUrl");
      var sigImage = document.getElementById("sig-image");
      var sigImagedoc = document.getElementById("signature_pad_image_document");
      var clearBtn = document.getElementById("sig-clearBtn");
      var submitBtn = document.getElementById("sig-submitBtn");
      clearBtn.addEventListener("click", function(e) {
        clearCanvas();
        sigText.innerHTML = "Data URL for your signature will go here!";
        sigImage.setAttribute("src", "");
        sigImagedoc.setAttribute("src", "");
      }, false);
      submitBtn.addEventListener("click", function(e) {
        var dataUrl = canvas.toDataURL();
        sigText.innerHTML = dataUrl; 
        sigImage.setAttribute("src", dataUrl);
        sigImagedoc.setAttribute("src", dataUrl);
  
        var buttonSendDoc = document.getElementById("send_document")
        buttonSendDoc.onclick = function () {
            ajax.jsonRpc('/send_sale', 'call', {url_signature: dataUrl,
                                            id_sale: id_sale});
            document.getElementById("alertSignatureSent").hidden = false;
          
        };
      }, false);
    
    })();
  
  
    const image_input = document.querySelector("#image_input");
    //var clearBtnfile = document.getElementById("sig_clearBtn_file");
    //var submitBtnfile = document.getElementById("sig_submitBtn_file");
    image_input.addEventListener("change", function() {
      //var sigImagedoc = document.getElementById("signature_pad_image_document");
      const reader = new FileReader();
      reader.addEventListener("load", () => {
      const uploaded_image = reader.result;
      document.querySelector("#display_image").style.backgroundImage = `url(${uploaded_image})`;
      //
      //clearBtnfile.addEventListener("click", function() {
      //  sigImagedoc.setAttribute("src", "");
      //  document.querySelector("#display_image").setAttribute("src", "");;
      //}, false);
  
      //submitBtnfile.addEventListener("click", function(e) {
      //  document.querySelector("#display_image").style.backgroundImage = `url(${uploaded_image})`;
      //  sigImagedoc.setAttribute("src", `url(${uploaded_image})`);
      //}, false);
    });
      reader.readAsDataURL(this.files[0]);
    });
  
    // Hidden options
    var draw_select_option = document.getElementById("signature_draw_option")
    var upload_select_option = document.getElementById("signature_upload_option")
  
    upload_select_option.addEventListener("click", function() {
      console.log("upload_select_option")
      document.getElementById("menu_signature_pad").hidden = true;
      console.log("upload_select_option")
      document.getElementById("menu_signature_upload").hidden = false;
      console.log("upload_select_option")
    }, false);
  
    draw_select_option.addEventListener("click", function() {
      console.log("draw_select_option")
      document.getElementById("menu_signature_upload").hidden = true;
      console.log("draw_select_option")
      document.getElementById("menu_signature_pad").hidden = false;
      console.log("draw_select_option")
    }, false);
  
  });
