# Formific Item Catalog App

## Description
This application generates a web catalog of items called __Formific__. I have named my catalog __Formific__ because it is specificallyintended to document things (objects, artworks, crafts) that have been made by hand. Users can log in using their Google or FaceBook logins and add their own items to the catalog. Users can also edit or delete their items if they are logged in. The app also provides JSON endpoints.

This is the fourth project that I have completed for the [Udacity Full Stack Web Developer Nanodegree Program](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

## Instructions
1. Install [VirtualBox](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) for your operating system.
2. Download and install [Vagrant](https://www.vagrantup.com/downloads.html) for your operating system.
3. Fork and clone this repository.
4. Open Terminal (if using a Mac) or Git Bash (if using Windows), and `cd` into the folder called `vagrant`.
5. Run the command `vagrant up`.
6. Then run the command `vagrant ssh`.
7. To populate the app with some starter database items run `python catalog/starter_items.py`
8. Then launch the app with `python catalog/formific.py`
9. Now go to [http://localhost:8000/formific](http://localhost:8000/formific) to see the app in action.
10. Login with either your Google of FaceBook credentials to add your own items to the catalog.

## License

MIT License

Copyright (c) 2018 Yshia Wallace

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
