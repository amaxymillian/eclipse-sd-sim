//Needs comment Header

//No global variable needed?
var blueprintDrawSemaphore = false;

const SEARCH_WIDTH = .01; // As a percentage of canvas, how wide to search for banding boxes



class Ship {
    constructor(shipType) {
        this.shipType = shipType;
        this.parts = [];
    }

    get shipType() {
        return this.shipType;
    }

    set shipType(newShipType) {
        this.shipType = newShipType;
    }



}


function selectBlueprint(blueprintName) {
  const shipBlueprintCanvas = document.getElementById('shipBlueprintCanvas');
  const width = shipBlueprintCanvas.width;
  const height = shipBlueprintCanvas.height;

  const context = shipBlueprintCanvas.getContext('2d');

  // Reset our canvas before drawing the new blueprint
  context.clearRect(0, 0, shipBlueprintCanvas.width, shipBlueprintCanvas.height)

  //Load new image only if the semaphore is up, update the canvas side, and paint.
  if (!blueprintDrawSemaphore) {
    const shipBluePrintLoadingDiv = document.getElementById("shipBluePrintLoadingDiv");
    //shipDesigner.removeAttribute("hidden");
    shipBluePrintLoadingDiv.style.display = "block";
    
    const image = new Image();
    image.src = '/static/images/blueprints/' + blueprintName + '.png'; 

    shipBlueprintCanvas.width = image.width;
    shipBlueprintCanvas.height = image.height;
    image.onload = function() {
      let shipBlueprintCanvas = document.getElementById('shipBlueprintCanvas');
      let context = shipBlueprintCanvas.getContext('2d');
      context.drawImage(image, 0, 0, image.width, image.height);
      let shipBluePrintLoadingDiv = document.getElementById("shipBluePrintLoadingDiv");
      shipBluePrintLoadingDiv.style.display = "none";
    }
  }  
}

const SearchDirection = {
    Right: Symbol("right"),
    Left: Symbol("left"),
    Up: Symbol("up"),
    Down: Symbol("down")
};

function getWhitePixelLength(direction, imageData, x, y) {
    data = imageData.data;
    width = imageData.width;
    height = imageData.height;
    
    //data is an Uint8ClampedArray object
    let count = 0
    let i = (y*width+x)*4;
    switch(direction) {
    case SearchDirection.Right:
        while(data[i+4] > 200 && data[i+5] > 200 && data[i+6] > 200) {
            //Need to check for perpendicular white lines which could indicate we're a subset square
            count+=1;
            i+=4;
        }
        break;
    case SearchDirection.Left:
        while(i >= 4 && data[i-4] > 200 && data[i-3] > 200 && data[i-2] > 200) {
            count+=1;
            i-=4;
        }
        break;
    case SearchDirection.Down:
        while(data[i+width * 4] > 200 && 
        data[i+Math.trunc(width * 4) + 1] > 200 && 
        data[i+Math.trunc(width * 4) + 2] > 200) {
            count+=1;
            i+=Math.trunc(width * 4);
        }
        break;
    case SearchDirection.Up:
        while(i-width * 4 >= 0 && data[i-width * 4] > 200 && 
        data[i-Math.trunc(width * 4) + 1] > 200 && 
        data[i-Math.trunc(width * 4) + 2] > 200) {
            count+=1;
            i-=Math.trunc(width * 4);
        }
        break;
    }
    return count
}

function getBluePrintPartBoundingBoxes(shipBlueprintCanvas, context) {
    // Examine the blueprint canvas pixel by pixel to identify the upper right and lower left corners of all
    // the part outlines in the canvas.  They're white boxes with blue through to grey pixels adjecent.
    // There's probably a library out there that does this already...?
    let { width, height } = shipBlueprintCanvas.getBoundingClientRect(); //These can/will be floats
    const imageData = context.getImageData(0, 0, width, height);
    const data = imageData.data;

    //Redefine width/height to be the actual width/height of the image data grabbed as this should(?) 
    //be an int value...
    width = imageData.width;
    height = imageData.height;
    //console.log("imageData width: " + width + ", height: " + height);

    // For debugging - uncomment this to log to console the pixel at the cursor position.  Slightly funky
    // in execution (I think...) due to pixel antialiasing performed by dynamically resized canvases.
    shipBlueprintCanvas.addEventListener( 'mousemove', event => {
    
        const bb = shipBlueprintCanvas.getBoundingClientRect();
        
        const x = Math.trunc(event.clientX - bb.left);
        const y = Math.trunc(event.clientY - bb.top);
        const pixel = context.getImageData(x,y,1,1);
        let data = pixel.data;

        let pixelR = data[0];
        let pixelG = data[1];
        let pixelB = data[2];
        let pixelA = data[3] / 255;
        
        
        console.log("Pixel (" + x + "," + y + "): (" + pixelR + "," + pixelG + "," + pixelB + "," + 
                        pixelA + ")");
      
    });
    

    // Iterate over pixels.  color data is in RGB format.
    //The top 15% of the canvas can never contain a candidate square, avoid this
    for (let y = Math.trunc(height*.15); y < height; y += 1) {
        
        for (let x = 0; x < width; x += 1) {
            
            //height and width can be floating values as the webpage is resized
            let i = (y*width+x)*4;
            let pixelR = data[i];
            let pixelG = data[i+1];
            let pixelB = data[i+2];
            let pixelA = data[i+3] / 255;
            
            if(pixelR > 200 && pixelG > 200 && pixelB > 200) {
                //console.log("-> Pixel (" + x + "," + y + "): (" + pixelR + "," + pixelG + "," + pixelB + ")");

                //If the pixel 25% of the width of this canvas to the right of this pixel is a candidate pixel, 
                //and 10% of the height of this canvas below is ALSO a candidate pixel
                //color *this* pixel green
                if(data[i+Math.trunc(width * .25 * 4)] > 220 && 
                    data[i+Math.trunc(width * .25 * 4) + 1] > 220 && 
                    data[i+Math.trunc(width * .25 * 4) + 2] > 220 &&
                    data[i+Math.trunc((height * .10) * width * 4)] &&
                    data[i+Math.trunc((height * .10) * width * 4) + 1] &&
                    data[i+Math.trunc((height * .10) * width * 4) + 2] ){

                    // Get the length of white pixels to the right and below from this point to check for a rect
                    let horizLength = getWhitePixelLength(SearchDirection.Right, imageData, x, y);
                    let vertLength = getWhitePixelLength(SearchDirection.Down, imageData, x, y);

                    if(horizLength > (width * .1) && vertLength > (height * .1) ) {
                        //candidate corner
                        
                        //Check if we're a square
                        bottomLength = getWhitePixelLength(SearchDirection.Right, imageData, x, y+vertLength);
                        rightLength = getWhitePixelLength(SearchDirection.Down, imageData, x+horizLength, y);

                        console.log("candidate corner (" + x + "," + y + ") has horiz,vert length of: " 
                                        + horizLength + ", " + vertLength + " and bottom,right length of: "
                                        + bottomLength + ", " + rightLength);
                        
                        data[i] = 0;
                        data[i+1] = 255;
                        data[i+2] = 0;
                        data[i+3] = 255;
                    }
                }
                else {
                    data[i] = 255;
                    data[i+1] = 0;
                    data[i+2] = 0;
                    data[i+3] = 255;
                }

            }
   
        }
        
    }
    const outputData = context.putImageData(imageData, 0, 0);

    /*
    //Create banding boxes for all squares (target locations for part) on this ship
    //TODO: check to see if part fitting would be allowed - this would require python calls to our py code
    // or building javascript functions that can calculate power requirements / drive requirements/ etc.
    tracking.Fast.THRESHOLD = 100;
    //context.drawImage(image, 0, 0, width, height);

    //const imageData = context.getImageData(0, 0, width, height);
    let gray = tracking.Image.grayscale(data, width, height);
    let corners = tracking.Fast.findCorners(gray, Math.trunc(width), Math.trunc(height));

    for (var i = 0; i < corners.length; i += 2) {
        context.fillStyle = '#f00';
        context.fillRect(corners[i], corners[i + 1], 3, 3);
    } 
    */   


}

function showShipDesigner() {
  //alert("clicked!");
  const shipDesigner = document.getElementById("shipDesigner");
  //shipDesigner.removeAttribute("hidden");
  shipDesigner.style.display = "block";
}

function addPartToShip(partName) {
  //Create a highlightable area of the canvas and write the name of the part as a hidden tag
  var shipBlueprintCanvas = document.getElementById('shipBlueprintCanvas');
  var width = shipBlueprintCanvas.width;
  var height = shipBlueprintCanvas.height;

  var context = shipBlueprintCanvas.getContext('2d');

  // Load image as new each time?
  /*
  const image = new Image();
  image.src = '/static/images/parts/' + partName + '.png'; 

  context.drawImage(image, 0, 0, width, height);
  */

  
  getBluePrintPartBoundingBoxes(shipBlueprintCanvas, context);



}