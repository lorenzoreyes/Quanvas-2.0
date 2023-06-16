from packages import *

style = '''\
<!DOCTYPE html>
<html>
<head>
<style>
body {
  font-family: 'Trebuchet MS', sans-serif;
}
.header {
  width: 100%;
  margin-left: auto; 
  margin-right: auto;
  border-radius: 10px;
  padding: 1px;
  text-align: center;
  background-color: black;
  color: rgb(60, 179, 113);
  font-size: 32px;
}
tr:hover {background-color:rgb(0,0,0); color:rgb(60, 179, 113);}
/* Create two equal columns that sits next to each other */
table, th, td, tr {
  font-size: 12px;
  border-radius: 5px;
  border: none;
  padding: 1px;
  border-collapse: collapse;
  text-align: center;   
  white-space: nowrap;
  margin-left: auto; 
  margin-right: auto;
}
th {
  height: 16px;
}
td {
  font-weight: bold;
}
</style>
</head>
<body>
'''
end_html =''' 
</body>
</html>'''


highlight = """<div class="header">
                <h2>&lt;Quanvas/&gt;</h2>
              </div> """

script = """
<script>
let slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
  showSlides(slideIndex += n);
}

function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");
  if (n > slides.length) {slideIndex = 1}    
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";  
  }
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";  
  dots[slideIndex-1].className += " active";
}
</script>
"""
