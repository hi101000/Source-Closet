const container = document.querySelector("#content");
const img = document.querySelector(".scaled");

let zoom = 1;
if(img){
    container.addEventListener('mouseenter', e => {
      // Code to execute when the mouse enters the element
      window.onscroll = function () {
            window.scrollTo(0,0);
        };
    });
    container.addEventListener('mouseleave', e=>{
        window.onscroll = function () { };
        zoom = 1;
        img.style.transform = `scale(${zoom})`;
    })
    container.addEventListener('wheel', e =>{
        img.style.transformOrigin = `${e.offsetX}px ${e.offsetY}px`;
        zoom += e.deltaY * -0.01;
        zoom = Math.min(Math.max(1, zoom), 5);
        img.style.transform = `scale(${zoom})`;
    });
}