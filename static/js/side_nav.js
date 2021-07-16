/* Set the width of the side navigation to 250px and the left margin of the page content to 250px and add a black background color to body */
function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
    document.body.style.backgroundColor = "rgba(0,0,0,0.4)";
    document.getElementById("btn-nav-open").style.opacity = "0";
    document.getElementById("btn-nav-close").style.opacity = "1";
  }
  
  /* Set the width of the side navigation to 0 and the left margin of the page content to 0, and the background color of body to white */
  function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("main").style.marginLeft = "0";
    document.body.style.backgroundColor = "rgb(240,240,240)";
    document.getElementById("btn-nav-open").style.opacity = "1";
    document.getElementById("btn-nav-close").style.opacity = "0";
  } 