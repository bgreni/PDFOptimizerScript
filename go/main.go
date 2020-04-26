package main

import (
	"fmt"
	"runtime"
	"time"
	"io/ioutil"
	"strings"
	"sync"
	"os/exec"
)

/**
An experimental Go version but it doesn't really do anything special
*/

func main() {
	var wg sync.WaitGroup
	runtime.GOMAXPROCS(runtime.NumCPU())
	start := time.Now()
	items, _ := ioutil.ReadDir("..")
	for _, item := range items {
		name := item.Name()
		if strings.HasSuffix(name, ".pdf")	{
			wg.Add(1)
			go func(filename string) {
				defer wg.Done()
				outFile := "out/" + filename
				cmd := exec.Command(
					"gs",
					"-sDEVICE=pdfwrite" ,
					"-dCompatibilityLevel=1.4",
					"-dPDFSETTINGS=/screen",
					"-dNOPAUSE",
					"-dQUIET",
					"-dBATCH",
					"-sOutputFile=\""+ outFile + "\"",
					"\"" + "../" + filename + "\"")
				err := cmd.Run()
				if err != nil {
					fmt.Println(err)
				}
			}(name)
		}
	}
	wg.Wait()
	t := time.Now()
	elapsed := t.Sub(start)
	fmt.Println(elapsed)
}
