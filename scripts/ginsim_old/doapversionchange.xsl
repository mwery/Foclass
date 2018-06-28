<?xml version='1.0'?>
<xsl:stylesheet 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:doap="http://usefulinc.com/ns/doap#"
	xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
	version="1.0">

<xsl:param name="GINsim.version"/> <!-- give it a value at run time  -->

<xsl:template match="*">
 <xsl:copy>
  <xsl:copy-of select="@*"/>
  <xsl:apply-templates/>
 </xsl:copy>
</xsl:template> 

<xsl:template match="doap:version">
 <xsl:copy>
  <xsl:choose>
   <xsl:when test="$GINsim.version != ''">
    <xsl:value-of select="$GINsim.version"/>
   </xsl:when>
   <xsl:otherwise>
    <xsl:apply-templates/>
   </xsl:otherwise>
  </xsl:choose>
 </xsl:copy>
</xsl:template> 

</xsl:stylesheet>
