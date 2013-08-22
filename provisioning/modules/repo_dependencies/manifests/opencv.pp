class repo_dependencies::opencv {

    include wget

    wget::fetch { "download_opencv_installer":
      source      => "https://raw.github.com/jayrambhia/Install-OpenCV/master/Ubuntu/opencv_latest.sh",
      destination => "/tmp/opencv_latest.sh",
    }

    file { "/tmp/opencv_latest.sh":
      mode => '0755',
    }

    exec { "install_opencv":
      command => "/bin/bash opencv_latest.sh",
      cwd => '/tmp'
    }

    Wget::Fetch["download_opencv_installer"] -> File["/tmp/opencv_latest.sh"] -> Exec["install_opencv"]
}
