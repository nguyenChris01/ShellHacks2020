#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>

// Function Prototype
void printAttributes(char name[], struct stat statBuff);

int main() {

  struct stat statBuff;
  int error;
  struct dirent *de;

  DIR * dir;
  dir = opendir(".");

  if (dir == NULL){
    printf("Could not open current directory\n");

    return 0;
  }

  while ((de = readdir(dir)) != NULL){
      error = stat(de->d_name, &statBuff);


  if (error == -1){
    printf("Error in stat\n");
    printf("Enter to continue...\n");
    error = getchar();

    return 1;
  }

  printAttributes(de->d_name, statBuff);
}
}

// printAttribute Function
void printAttributes(char *name, struct stat x){

  time_t t;
  char timeStr [100];

  printf("===================== File Name: %s =====================\n", name);
  printf("Device ID: %lu\n", x.st_dev);
  printf("File Serial Number: %lu\n", x.st_ino);
  printf("File User ID: %u\n", x.st_uid);
  printf("File Group ID: %u\n", x.st_gid);
  printf("File Mode: %u\n", x.st_mode);

  // Owner Permissions
  printf("Owner Permissions: ");
  if (x.st_mode & S_IRUSR)
    printf("Read ");
  if (x.st_mode & S_IWUSR)
    printf("Write ");
  if (x.st_mode & S_IXUSR)
    printf("Execute ");
  printf("\n");
  // Group Permissions
  printf("Group Permissions: ");
  if (x.st_mode & S_IRGRP)
    printf("Read ");
  if (x.st_mode & S_IWGRP)
    printf("Write ");
  if (x.st_mode & S_IXGRP)
    printf("Execute ");
  printf("\n");
  // Other Permissions
  printf("Other Permissions: ");
  if (x.st_mode & S_IROTH)
    printf("Read ");
  if (x.st_mode & S_IWOTH)
    printf("Write ");
  if (x.st_mode & S_IXOTH)
    printf("Execute ");
  printf("\n");

  // Creation || Modification || Last Accessed || File Size
printf("Date Created: %s", ctime(&x.st_ctime));
printf("Date Modified: %s", ctime(&x.st_mtime));
printf("Time file was last accessed: %s", ctime(&x.st_atime));
printf("File Size: %lu bytes", x.st_size);
printf("\n"); // New Line
}
