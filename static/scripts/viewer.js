const container = document.querySelector("#content");
const img = document.querySelector(".scaled");
let clicked = false
let xAxis;
let x;
let yAxis;
let y;

let zoom = 1;
if(img){
    //img.style.height = container.style.height
    container.addEventListener('mouseenter', e => {
      // Code to execute when the mouse enters the element
      window.onscroll = function () {
            window.scrollTo(0,window.scrollY);
        };
    });
    container.addEventListener('mouseleave', e=>{
        window.onscroll = function () { };
        zoom = 1;
        img.style.transform = `scale(${zoom})`;
    })
    container.addEventListener('wheel', e =>{
        img.style.transformOrigin = `${e.offsetX}px ${e.offsetY}px`;
        zoom += e.deltaY * -0.005;
        zoom = Math.min(Math.max(1, zoom), 5);
        img.style.transform = `scale(${zoom})`;
    });
        let isPanning = false;
    let startX, startY;
    let currentX = 0, currentY = 0;
    
    container.addEventListener('mousedown', (e) => {
      isPanning = true;
      startX = e.clientX - currentX;
      startY = e.clientY - currentY;
      container.style.cursor = 'grabbing';
    });
    
    img.addEventListener('mousemove', (e) => {
      if (!isPanning) return;
      currentX = e.clientX - startX;
      currentY = e.clientY - startY;
      img.style.left = `${currentX}px`;
      img.style.top = `${currentY}px`;
    });
    container.addEventListener('ondrag', (e) => {
      if (!isPanning) return;
      currentX = e.clientX - startX;
      currentY = e.clientY - startY;
      img.style.left = `${currentX}px`;
      img.style.top = `${currentY}px`;
    });
    
    container.addEventListener('mouseup', () => {
      isPanning = false;
      container.style.cursor = 'default';
    });
    
    container.addEventListener('mouseleave', () => {
        isPanning = false;
        img.style.left = `0px`;
        img.style.top = `0px`;
        container.style.cursor = 'default';
    });

}
else{
    //
}