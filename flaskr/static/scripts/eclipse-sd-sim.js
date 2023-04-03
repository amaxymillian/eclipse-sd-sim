//Needs comment Header

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

function getBluePrintPartBoundingBoxes(shipBlueprintCanvas, context) {
    // Examine the blueprint canvas pixel by pixel to identify the upper right and lower left corners of all
    // the part outlines in the canvas.  They're white boxes with blue through to grey pixels adjecent.
    // There's probably a library out there that does this already...?
    const { width, height } = shipBlueprintCanvas.getBoundingClientRect();
    const imageData = context.getImageData(0, 0, width, height).data;

    // Iterate over pixels.  color data is in RGB format.
    for (var y = 0; y < height; y += 1) {
        for (var x = 0; x < width; x += 1) {
            
            //height and width can be floating values as the webpage is resized
            let i = (y*Math.trunc(height)+x)*3;
            let pixelR = imageData[i];
            let pixelG = imageData[i+1];
            let pixelB = imageData[i+2];
            //if(pixelR > 220 && pixelG > 220 && pixelB > 220) {
            console.log("Pixel (" + y + "," + x + "): (" + pixelR + "," + pixelG + "," + pixelB + ")");
            //}
            
        }
        break;
    }


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

  /*
  //Create banding boxes for all squares (target locations for part) on this ship
  //TODO: check to see if part fitting would be allowed - this would require python calls to our py code
  // or building javascript functions that can calculate power requirements / drive requirements/ etc.
  tracking.Fast.THRESHOLD = 100;
  //context.drawImage(image, 0, 0, width, height);

  const imageData = context.getImageData(0, 0, width, height);
  const gray = tracking.Image.grayscale(imageData.data, width, height);
  const corners = tracking.Fast.findCorners(gray, width, height);

  for (var i = 0; i < corners.length; i += 2) {
    context.fillStyle = '#f00';
    context.fillRect(corners[i], corners[i + 1], 3, 3);
  }    
  */
  getBluePrintPartBoundingBoxes(shipBlueprintCanvas, context);



}