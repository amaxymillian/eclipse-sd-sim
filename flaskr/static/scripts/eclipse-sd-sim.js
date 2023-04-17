//Needs comment Header

//Enums
const SearchDirection = {
    Right: Symbol("right"),
    Left: Symbol("left"),
    Up: Symbol("up"),
    Down: Symbol("down")
};

const ShipType = {
    TERRAN_INTERCEPTOR: "Terran_Interceptor",
    TERRAN_CRUISER: "Terran_Cruiser",
    TERRAN_DREADNOUGHT: "Terran_Dreadnought",
    TERRAN_STARBASE: "Terran_Starbase",
    ERIDANI_INTERCEPTOR: "Eridani_Interceptor",
    ERIDANI_CRUISER: "Eridani_Cruiser",
    ERIDANI_DREADNOUGHT: "Eridani_Dreadnought",
    ERIDANI_STARBASE: "Eridani_Starbase",
    ORION_INTERCEPTOR: "Orion_Interceptor",
    ORION_CRUISER: "Orion_Cruiser",
    ORION_DREADNOUGHT: "Orion_Dreadnought",
    ORION_STARBASE: "Orion_Starbase",
    PLANTA_INTERCEPTOR: "Planta_Interceptor",
    PLANTA_CRUISER: "Planta_Cruiser",
    PLANTA_DREADNOUGHT: "Planta_Dreadnought",
    PLANTA_STARBASE: "Planta_Starbase"
};

const SEARCH_WIDTH = .01; // As a percentage of canvas, how wide to search for banding boxes
const WHITE_SENSITIVITY = 150;  //RGB threshold for tracking a 'white' pixel
/*
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
var selectedShip = new Ship()
*/

class BoundingBox {
    constructor(x, y, horizLength, vertLength) {
        this.x = x;
        this.y = y;
        this.horizLength = horizLength;
        this.vertLength = vertLength
    }
}

//No global variable needed?
var blueprintDrawSemaphore = false;


function selectBlueprint(blueprintName) {
  const shipBlueprintCanvas = document.getElementById('shipBlueprintCanvas');
  const width = shipBlueprintCanvas.width;
  const height = shipBlueprintCanvas.height;

  const context = shipBlueprintCanvas.getContext('2d');

  // Reset our canvas before drawing the new blueprint
  context.clearRect(0, 0, shipBlueprintCanvas.width, shipBlueprintCanvas.height)

  //Load new image only if the semaphore is up, update the canvas side, and paint.
  //if (!blueprintDrawSemaphore) {
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
  //}  
}



function getWhitePixelLength(direction, imageData, x, y) {
    data = imageData.data;
    width = imageData.width;
    height = imageData.height;
    
    //data is an Uint8ClampedArray object
    let count = 0
    let i = (y*width+x)*4;
    switch(direction) {
    case SearchDirection.Right:
        while(data[i+4] > WHITE_SENSITIVITY && data[i+5] > WHITE_SENSITIVITY 
            && data[i+6] > WHITE_SENSITIVITY) {
            //Need to check for perpendicular white lines which could indicate we're a subset square
            if(getWhitePixelLength(SearchDirection.Up, imageData, i, y) >5 ||
            getWhitePixelLength(SearchDirection.Down, imageData, i, y) >5 ) {
                console.log('SearchDirection.Right, perpendicular white line found?');
                return count
            }
            count+=1;
            i+=4;
        }
        break;
    case SearchDirection.Left:
        while(i >= 4 && data[i-4] > WHITE_SENSITIVITY && data[i-3] > WHITE_SENSITIVITY 
            && data[i-2] > WHITE_SENSITIVITY) {
            if(getWhitePixelLength(SearchDirection.Up, imageData, i, y) > 5 ||
            getWhitePixelLength(SearchDirection.Down, imageData, i, y) >5 ) {
                console.log('SearchDirection.Left, perpendicular white line found?');
                return count
            }
            count+=1;
            i-=4;
        }
        break;
    case SearchDirection.Down:
        while(data[i+width * 4] > WHITE_SENSITIVITY && 
        data[i+Math.trunc(width * 4) + 1] > WHITE_SENSITIVITY && 
        data[i+Math.trunc(width * 4) + 2] > WHITE_SENSITIVITY) {
            if(getWhitePixelLength(SearchDirection.Left, imageData, x, i) > 5 ||
            getWhitePixelLength(SearchDirection.Right, imageData, x, i) >5 ) {
                console.log('SearchDirection.Down, perpendicular white line found?');
                return count
            }
            count+=1;
            i+=Math.trunc(width * 4);
        }
        break;
    case SearchDirection.Up:
        while(i-width * 4 >= 0 && data[i-width * 4] > WHITE_SENSITIVITY && 
        data[i-Math.trunc(width * 4) + 1] > WHITE_SENSITIVITY && 
        data[i-Math.trunc(width * 4) + 2] > WHITE_SENSITIVITY) {
            if(getWhitePixelLength(SearchDirection.Left, imageData, x, i) > 5 ||
            getWhitePixelLength(SearchDirection.Right, imageData, x, i) >5 ) {
                console.log('SearchDirection.Down, perpendicular white line found?');
                return count
            }
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
    
    
    let boundingBoxArray = [];

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
            
            if(pixelR > WHITE_SENSITIVITY && pixelG > WHITE_SENSITIVITY && pixelB > WHITE_SENSITIVITY) {
                //console.log("-> Pixel (" + x + "," + y + "): (" + pixelR + "," + pixelG + "," + pixelB + ")");

                //If the pixel 20% of the width of this canvas to the right of this pixel is a candidate pixel, 
                //and 10% of the height of this canvas below is ALSO a candidate pixel
                if(data[i+Math.trunc(width * .20 * 4)] > WHITE_SENSITIVITY && 
                    data[i+Math.trunc(width * .20 * 4) + 1] > WHITE_SENSITIVITY && 
                    data[i+Math.trunc(width * .20 * 4) + 2] > WHITE_SENSITIVITY &&
                    data[i+Math.trunc((height * .10) * width * 4)] &&
                    data[i+Math.trunc((height * .10) * width * 4) + 1] &&
                    data[i+Math.trunc((height * .10) * width * 4) + 2] ){

                    // Get the length of white pixels to the right and below from this point to check for a rect
                    let horizLength = getWhitePixelLength(SearchDirection.Right, imageData, x, y);
                    let vertLength = getWhitePixelLength(SearchDirection.Down, imageData, x, y);

                    console.log("candidate corner (" + x + "," + y + ") has horiz,vert length of: " 
                                        + horizLength + ", " + vertLength + ".");

                    if(horizLength > (width * .1) && vertLength > (height * .1) ) {
                        //candidate corner
                        
                        //Check if we're a square
                        bottomLength = getWhitePixelLength(SearchDirection.Right, imageData, x, y+vertLength);
                        rightLength = getWhitePixelLength(SearchDirection.Down, imageData, x+horizLength, y);

                        console.log("... and bottom,right length of: " + bottomLength + ", " + rightLength);

                        if (Math.abs(horizLength - bottomLength) / horizLength < .1 && 
                            Math.abs(vertLength - rightLength) / vertLength < .1 ) {
                            /* This is a selection box, draw it to canvas and create it as a clickable region */
                            console.log("Adding selection box at (" + x + "," + y + " of dimesions " 
                            + horizLength + "," + vertLength)
                            boundingBoxArray.push(new BoundingBox(x, y, horizLength, vertLength));
                            
                        }
                        else {
                        
                            data[i] = 0;
                            data[i+1] = 255;
                            data[i+2] = 0;
                            data[i+3] = 255;
                        }
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
    //const outputData = context.putImageData(imageData, 0, 0);

    //Create banding boxes for all squares (target locations for part) on this ship
    //TODO: check to see if part fitting would be allowed - this would require python calls to our py code
    // or building javascript functions that can calculate power requirements / drive requirements/ etc.
    rectContext = shipBlueprintCanvas.getContext("2d");
    rectContext.strokeStyle = "blue";
    rectContext.lineWidth = "6";
    for(let i = 0; i < boundingBoxArray.length; i++) {
        rectContext.beginPath();
        rectContext.rect(boundingBoxArray[i].x, boundingBoxArray[i].y, 
            boundingBoxArray[i].horizLength, boundingBoxArray[i].vertLength);
        rectContext.stroke();
    }
    
    


}

function showPrimaryDiv(divToShow) {
  const shipDesigner = document.getElementById("shipDesigner");
  const battleSimulator = document.getElementById("battleSimulator");
  //shipDesigner.removeAttribute("hidden");
  switch(divToShow){
    case "shipDesigner":
        shipDesigner.style.display = "block";
        battleSimulator.style.display = "none";
        break;
    case "battleSimulator":
        shipDesigner.style.display = "none";
        battleSimulator.style.display = "block";
        break;
  }
  
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