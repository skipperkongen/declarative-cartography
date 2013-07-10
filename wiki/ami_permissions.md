# Adding launch permissions for Kostas AMI for CVL

I (Kostas) have created an AMI (ami-05677a71) for CVL under my account. It is a highmemory (m2.xlarge) instance running Linux. Marcos has some credits we can use for research. I'll make my AMI launchable by Marcos, so that we can test CVL "for free". This is how: http://aws.amazon.com/articles/530

List my AMI's

```
ec2-describe-images -o self
```

Give permission to Marcos to launch the AMI:

```
ec2-modify-image-attribute ami-05677a71 -l -a [MarcosAccountID]
```

Check that Marcos got permissions:

```
ec2-describe-image-attribute ami-05677a71 -l
```